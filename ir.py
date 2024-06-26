#!/usr/bin/env python3

"""Intermediate Representation
Could be improved by relying less on class hierarchy and more on string tags 
and/or duck typing. Includes lowering and flattening functions. Every node must
have a lowering function or a code generation function (codegen functions are
in a separate module though)."""

from codegenhelp import *

# UTILITIES

tempcount = 0


def new_temporary(symtab, type):
    global tempcount
    temp = Symbol(name='t' + str(tempcount), stype=type, alloct='reg')
    tempcount += 1
    return temp


# TYPES

# NOTE: the type system is very simple, so that we don't need explicit cast
# instructions or too much handling in the codegen phase.
# Basically, the type system always behaves as every term of an expression was
# casted to the biggest type available, and the result is then casted to the
# biggest of the types of the terms.
# Also, no handling for primitive types that do not fit in a single machine
# register is provided.


BASE_TYPES = ['Int', 'Label', 'Struct', 'Function']
TYPE_QUALIFIERS = ['unsigned']


class Type:
    def __init__(self, name, size, basetype, qualifiers=None):
        if qualifiers is None:
            qualifiers = []
        self.size = size
        self.basetype = basetype
        self.qual_list = qualifiers
        self.name = name if name else self.default_name()

    def default_name(self):
        n = ''
        if 'unsigned' in self.qual_list:
            n += 'u'
        n += 'int'  # no float types exist at the moment
        n += repr(self.size)
        n += '_t'
        return n


class ArrayType(Type):
    def __init__(self, name, dims, basetype):
        """dims is a list of dimensions: dims = [5]: array of 5 elements;
        dims = [5, 5]: 5x5 matrix; and so on"""
        self.dims = dims
        super().__init__(name, reduce(lambda a, b: a * b, dims) * basetype.size, basetype)
        self.name = name if name else self.default_name()

    def default_name(self):
        return self.basetype.name + repr(self.dims)


class StructType(Type):  # currently unused
    def __init__(self, name, size, fields):
        self.fields = fields
        realsize = sum([f.size for f in self.fields])
        super().__init__(name, realsize, 'Struct', [])

    def get_size(self):
        return sum([f.size for f in self.fields])


class LabelType(Type):
    def __init__(self):
        super().__init__('label', 0, 'Label', [])
        self.ids = 0

    def __call__(self, target=None):
        self.ids += 1
        return Symbol(name='label' + repr(self.ids), stype=self, value=target)


class FunctionType(Type):
    def __init__(self):
        super().__init__('function', 0, 'Function', [])


class PointerType(Type):
    def __init__(self, ptrto):
        """ptrto is the type of the object that this pointer points to."""
        super().__init__('&' + ptrto.name, 32, 'Int', ['unsigned'])
        self.pointstotype = ptrto


TYPENAMES = {
    'int': Type('int', 32, 'Int'),
    'short': Type('short', 16, 'Int'),
    'char': Type('char', 8, 'Int'),
    'uchar': Type('uchar', 8, 'Int', ['unsigned']),
    'uint': Type('uint', 32, 'Int', ['unsigned']),
    'ushort': Type('ushort', 16, 'Int', ['unsigned']),
    # 'float': Type('float', 32, 'Float'),
    'label': LabelType(),
    'function': FunctionType(),
}

ALLOC_CLASSES = ['global', 'auto', 'reg', 'imm']


class Symbol:
    """There are 4 classes of allocation for symbols:\n
    - allocation to a register ('reg')
    - allocation to an arbitrary memory location, in the current stack frame
      ('auto') or in the data section ('global')
    - allocation to an immediate ('imm')"""

    def __init__(self, name, stype, value=None, alloct='auto'):
        self.name = name
        self.stype = stype
        self.value = value  # if not None, it is a constant
        self.alloct = alloct
        self.allocinfo = None

    def set_alloc_info(self, allocinfo):
        self.allocinfo = allocinfo

    def __repr__(self):
        base = self.alloct + ' ' + self.stype.name + ' ' + self.name + \
               (self.value if type(self.value) == str else '')
        if self.allocinfo is not None:
            base = base + "; " + repr(self.allocinfo)
        return base


class SymbolTable(list):
    def find(self, name):
        print('Looking up', name)
        for s in self:
            if s.name == name:
                return s
        print('Looking up failed!')
        return None

    def __repr__(self):
        res = 'SymbolTable:\n'
        for s in self:
            res += repr(s) + '\n'
        return res

    def exclude(self, barred_types):
        return [symb for symb in self if symb.stype not in barred_types]


# IRNODE

class IRNode:  # abstract
    def __init__(self, parent=None, children=None, symtab=None):
        self.parent = parent
        if children:
            self.children = children[:]
            for c in self.children:
                try:
                    c.parent = self
                except Exception:
                    pass
        else:
            self.children = []
        self.symtab = symtab

    def __repr__(self):
        try:
            label = self.get_label().name + ': '
        except Exception:
            label = ''
            pass
        try:
            hre = self.human_repr()
            return label + hre
        except Exception:
            pass

        attrs = {'body', 'cond', 'value', 'thenpart', 'elsepart', 'symbol', 'call', 'step', 'expr', 'target', 'defs',
                 'global_symtab', 'local_symtab', 'offset','start_assign',
                 'unroll_remainder_statlist','remainder_for'} & set(dir(self))

        res = repr(type(self)) + ' ' + repr(id(self)) + ' {\n'
        if self.parent is not None:
            res += 'parent = ' + repr(id(self.parent)) + '\n'
        else:
            # a missing parent is not a bug only for the root node, but at this
            # level of abstraction there is no way to distinguish between the root
            # node and a node with a missing parent
            res += '                                                                      <<<<<----- BUG? MISSING PARENT\n'

        res = label + res

        # print 'NODE', type(self), id(self)
        if 'children' in dir(self) and len(self.children):
            res += '\tchildren:\n'
            for node in self.children:
                rep = repr(node)
                res += '\n'.join(['\t' + s for s in rep.split('\n')]) + '\n'
        for d in attrs:
            node = getattr(self, d)
            rep = repr(node)
            res += '\t' + d + ': ' + '\n'.join(['\t' + s for s in rep.split('\n')]) + '\n'
        res += '}'
        return res

    def descendants(self):
        u = [self] 
        for c in self.children:
            u += c.descendants()
        return u
    

    def navigate(self, action):
        attrs = {'body', 'cond', 'value', 'thenpart', 'elsepart', 'symbol', 'call', 'step', 'expr', 'target', 'defs',
                 'global_symtab', 'local_symtab', 'offset', 'start_assign',
                 'unroll_remainder_statlist','remainder_for'} & set(dir(self))
        if 'children' in dir(self) and len(self.children):
            print('navigating children of', type(self), id(self), len(self.children))
            for node in self.children:
                try:
                    node.navigate(action)
                except Exception:
                    pass
        for d in attrs:
            try:
                getattr(self, d).navigate(action)
                print('successfully navigated attr ', d, ' of', type(self), id(self))
            except Exception:
                pass
        action(self)

    def replace(self, old, new):
        new.parent = self
        if 'children' in dir(self) and len(self.children) and old in self.children:
            self.children[self.children.index(old)] = new
            return True
        attrs = {'body', 'cond', 'value', 'thenpart', 'elsepart', 'symbol', 'call', 'step', 'expr', 'target', 'defs',
                 'global_symtab', 'local_symtab', 'offset','start_assign',
                 'unroll_remainder_statlist','remainder_for'} & set(dir(self))
        for d in attrs:
            try:
                if getattr(self, d) == old:
                    setattr(self, d, new)
                    return True
            except Exception:
                pass
        return False

    def get_function(self):
        if not self.parent:
            return 'global'
        elif type(self.parent) == FunctionDef:
            return self.parent
        else:
            return self.parent.get_function()

    def get_label(self):
        raise NotImplementedError

    def human_repr(self):
        raise NotImplementedError


# CONST and VAR

class Const(IRNode):
    def __init__(self, parent=None, value=0, symb=None, symtab=None):
        super().__init__(parent, None, symtab)
        self.value = value
        self.symbol = symb

    def is_const(self):
        return True
    
    def get_const_value(self):
        return self.value

    def lower(self):
        if self.symbol is None:
            new = new_temporary(self.symtab, TYPENAMES['int'])
            loadst = LoadImmStat(dest=new, val=self.value, symtab=self.symtab)
        else:
            new = new_temporary(self.symtab, self.symbol.stype)
            loadst = LoadStat(dest=new, symbol=self.symbol, symtab=self.symtab)
        return self.parent.replace(self, StatList(children=[loadst], symtab=self.symtab))


class Var(IRNode):
    """loads in a temporary the value pointed to by the symbol"""

    def __init__(self, parent=None, var=None, symtab=None):
        super().__init__(parent, None, symtab)
        self.symbol = var

    def is_const(self):
        return False

    def collect_uses(self):
        return [self.symbol]

    def lower(self):
        """Var translates to a load statement to the same temporary that is used in
        a following stage for doing the computations (destination())"""
        new = new_temporary(self.symtab, self.symbol.stype)
        loadst = LoadStat(dest=new, symbol=self.symbol, symtab=self.symtab)
        return self.parent.replace(self, StatList(children=[loadst], symtab=self.symtab))


class ArrayElement(IRNode):
    """loads in a temporary the value pointed by: the symbol + the index"""

    def __init__(self, parent=None, var=None, offset=None, symtab=None):
        """offset can NOT be a list of exps in case of multi-d arrays; it should
        have already been flattened beforehand"""
        super().__init__(parent, [offset], symtab)
        self.symbol = var
        self.offset = offset

    def collect_uses(self):
        a = [self.symbol]
        a += self.offset.collect_uses()
        return a

    def lower(self):
        global TYPENAMES
        dest = new_temporary(self.symtab, self.symbol.stype.basetype)
        off = self.offset.destination()

        statl = [self.offset]

        ptrreg = new_temporary(self.symtab, PointerType(self.symbol.stype.basetype))
        loadptr = LoadPtrToSym(dest=ptrreg, symbol=self.symbol, symtab=self.symtab)
        src = new_temporary(self.symtab, PointerType(self.symbol.stype.basetype))
        add = BinStat(dest=src, op='plus', srca=ptrreg, srcb=off, symtab=self.symtab)
        statl += [loadptr, add]

        statl += [LoadStat(dest=dest, symbol=src, symtab=self.symtab)]
        return self.parent.replace(self, StatList(children=statl, symtab=self.symtab))


# EXPRESSIONS

class Expr(IRNode):  # abstract
    def get_operator(self):
        return self.children[0]

    def collect_uses(self):
        uses = []
        for c in self.children:
            try:
                uses += c.collect_uses()
            except AttributeError:
                pass
        return uses


class BinExpr(Expr):
    def get_operands(self):
        return self.children[1:]

    def is_const(self):
        return self.children[1].is_const() and self.children[2].is_const()

    def get_const_value(self):
        if(self.children[0] == 'minus'):
            return self.children[1].get_const_value() - self.children[2].get_const_value()
        if(self.children[0] == 'times'):
            return self.children[1].get_const_value() * self.children[2].get_const_value()
        if(self.children[0] == 'slash'):
            return self.children[1].get_const_value() / self.children[2].get_const_value()
        return self.children[1].get_const_value() + self.children[2].get_const_value()

    def lower(self):
        srca = self.children[1].destination()
        srcb = self.children[2].destination()

        # Type promotion.
        if ('unsigned' in srca.stype.qual_list) and ('unsigned' in srcb.stype.qual_list):
            desttype = Type(None, max(srca.stype.size, srcb.stype.size), 'Int', ['unsigned'])
        else:
            desttype = Type(None, max(srca.stype.size, srcb.stype.size), 'Int')

        dest = new_temporary(self.symtab, desttype)

        stmt = BinStat(dest=dest, op=self.children[0], srca=srca, srcb=srcb, symtab=self.symtab)
        statl = [self.children[1], self.children[2], stmt]
        return self.parent.replace(self, StatList(children=statl, symtab=self.symtab))


class UnExpr(Expr):
    def get_operand(self):
        return self.children[1]

    def is_const(self):
        return self.children[1].is_const()

    def get_const_value(self):
        if(self.children[0] == 'minus'):
            return (-self.children[1].get_const_value())
        return self.children[1].get_const_value()

    def lower(self):
        src = self.children[1].destination()
        dest = new_temporary(self.symtab, src.stype)
        stmt = UnaryStat(dest=dest, op=self.children[0], src=src, symtab=self.symtab)
        statl = [self.children[1], stmt]
        return self.parent.replace(self, StatList(children=statl, symtab=self.symtab))


class CallExpr(Expr):
    def __init__(self, parent=None, function=None, parameters=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.symbol = function
        # parameters are ignored
        if parameters:
            self.children = parameters[:]
        else:
            self.children = []


# STATEMENTS

class Stat(IRNode):  # abstract
    def __init__(self, parent=None, children=None, symtab=None):
        super().__init__(parent, children, symtab)
        self.label = None

    def set_label(self, label):
        self.label = label
        label.value = self  # set target

    def get_label(self):
        return self.label

    def collect_uses(self):
        return []

    def collect_kills(self):
        return []


class CallStat(Stat):
    """Procedure call"""

    def __init__(self, parent=None, call_expr=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.call = call_expr
        self.call.parent = self

    def collect_uses(self):
        return self.call.collect_uses() + self.symtab.exclude([TYPENAMES['function'], TYPENAMES['label']])

    def lower(self):
        dest = self.call.symbol
        bst = BranchStat(target=dest, symtab=self.symtab, returns=True)
        return self.parent.replace(self, bst)


class IfStat(Stat):
    def __init__(self, parent=None, cond=None, thenpart=None, elsepart=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.cond = cond
        self.thenpart = thenpart
        self.elsepart = elsepart
        self.cond.parent = self
        self.thenpart.parent = self
        if self.elsepart:
            self.elsepart.parent = self

    def lower(self):
        exit_label = TYPENAMES['label']()
        exit_stat = EmptyStat(self.parent, symtab=self.symtab)
        exit_stat.set_label(exit_label)
        if self.elsepart:
            then_label = TYPENAMES['label']()
            self.thenpart.set_label(then_label)
            branch_to_then = BranchStat(None, self.cond.destination(), then_label, self.symtab)
            branch_to_exit = BranchStat(None, None, exit_label, self.symtab)
            stat_list = StatList(self.parent,
                                 [self.cond, branch_to_then, self.elsepart, branch_to_exit, self.thenpart, exit_stat],
                                 self.symtab)
            return self.parent.replace(self, stat_list)
        else:
            branch_to_exit = BranchStat(None, self.cond.destination(), exit_label, self.symtab, negcond=True)
            stat_list = StatList(self.parent, [self.cond, branch_to_exit, self.thenpart, exit_stat], self.symtab)
            return self.parent.replace(self, stat_list)


class WhileStat(Stat):
    def __init__(self, parent=None, cond=None, body=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.cond = cond
        self.body = body
        self.cond.parent = self
        self.body.parent = self

    def lower(self):
        entry_label = TYPENAMES['label']()
        exit_label = TYPENAMES['label']()
        exit_stat = EmptyStat(self.parent, symtab=self.symtab)
        exit_stat.set_label(exit_label)
        self.cond.set_label(entry_label)
        branch = BranchStat(None, self.cond.destination(), exit_label, self.symtab, negcond=True)
        loop = BranchStat(None, None, entry_label, self.symtab)
        stat_list = StatList(self.parent, [self.cond, branch, self.body, loop, exit_stat], self.symtab)
        return self.parent.replace(self, stat_list)


class ForStat(Stat):  # incomplete
    def __init__(self,target=None, parent=None, op=None, start_exp=None, cond_expr=None, step_exp=None, body=None, symtab=None):
        super().__init__(parent, [], symtab)

        start_assign = AssignStat(target=target, expr=start_exp, symtab=symtab)
        self.start_assign = start_assign
        step = AssignStat(target=target, expr=step_exp, symtab=symtab)
        var = Var(var=target, symtab=symtab)
        cond = BinExpr(children=[op, var, cond_expr], symtab=symtab)

        self.saved_var = var
        self.saved_symb = target

        self.cond = cond
        self.step = step
        self.body = body
        
        self.start_assign.parent = self
        self.cond.parent = self
        self.step.parent = self
        self.body.parent = self
        self.unroll_remainder_statlist = StatList(self,[],self.symtab)
        self.remainder_for = StatList(self,[],self.symtab)

        #self.strip_mine(2)

    # def symb_modified_in_body(self,symb):
    #     statements = self.body.descendants()
    #     print("descendants")
    #     for s in statements:
    #         if isinstance(s, AssignStat):
    #             if s.symbol==symb:
    #                 return True
    #     return False

    def unroll(self, unroll_factor=None):
        #verify that the condition is constant
        cond_operand = self.cond.get_operands()[1]
        is_constant = cond_operand.is_const()
        if(is_constant):
            print('END CONSTANT')
        else:
            print('END CONTAINS VARIABLE')
            return
        end_value = cond_operand.get_const_value()


        #verify that the step is constant
        step = self.step.expr.get_operands()[1]
        is_constant = step.is_const()
        if(is_constant):
            print("STEP CONSTANT")
        else:
            print("STEP NOT CONSTANT")
            return
        step_value = step.get_const_value()

        #verify that the step is constant
        start_exp = self.start_assign.expr
        is_const = start_exp.is_const()
        if(is_constant):
            print('START CONSTANT')
        else:
            print('START NOT CONSTANT')
            return
        start_value = start_exp.get_const_value()


        #check if the number of iteration is lower than unroll factor
        numb_of_iteration = (end_value-start_value)/step_value  
        if(numb_of_iteration<unroll_factor):
            unroll_factor = int(numb_of_iteration)
            remainder = 0
            
        print("start %d" %start_value)
        print("end %d" %end_value)
        print("step %d" %step_value)


        #modify the end value if there is a remainder
        remainder = end_value%unroll_factor
        if(remainder != 0):
            new_value = end_value-(step_value*remainder)
            new_end_const = Const(parent=self.cond, value=new_value ,symtab=self.symtab)
            self.cond.children[2] = new_end_const

        #multiply body
        body_copy = self.body
        new_body = StatList(self,[],self.symtab)
        for i in range(unroll_factor):
            new_body.append(body_copy)
            new_body.append(self.step)

        #add the remainder statlist
        for i in range(remainder):
            self.unroll_remainder_statlist.append(body_copy)

        
        print('NEW BODY AFTER THE UNROLLING MULTIPLY')
        print(new_body)
        self.body = new_body
        self.body.parent = self 

    def strip_mine(self, strip_factor=None):

        print('\nSTARTING STRIP MINING\n')    

        #verify that the condition is constant
        cond_operand = self.cond.get_operands()[1]
        is_constant = cond_operand.is_const()
        if(is_constant):
            print('END CONSTANT')
        else:
            print('END CONTAINS VARIABLE')
            return
        end_value = cond_operand.get_const_value()

        #verify that the step is constant
        step = self.step.expr.get_operands()[1]
        is_constant = step.is_const()
        if(is_constant):
            print("STEP CONSTANT")
        else:
            print("STEP NOT CONSTANT")
            return
        step_value = step.get_const_value()

        #verify that the step is constant
        start_exp = self.start_assign.expr
        is_const = start_exp.is_const()
        if(is_constant):
            print('START CONSTANT')
        else:
            print('START NOT CONSTANT')
            return
        start_value = start_exp.get_const_value()



        ###creating outer for loop
        #create new induction variable
        alloct= 'auto'
        name = 'tmp_variable_for_strip_mining'
        type = TYPENAMES['int']
        new_symb = Symbol(name, type, alloct=alloct)
        self.symtab.append(new_symb)

        #find the parent block and append the variable in their symtab
        p = self.parent
        while True:
            if(isinstance(p,Block)):
                #append
                p.symtab.append(new_symb)
                break
            else:
                p = p.parent



        outer_ind_var = Var(var=new_symb, symtab=self.symtab)
        outer_ind_var_for_inner_assign = Var(var=new_symb, symtab=self.symtab)
        outer_ind_var_for_inner_cond = Var(var=new_symb, symtab=self.symtab)
        
        strip_factor_const = Const(parent=None,value=strip_factor,symtab=self.symtab)
        strip_factor_const2 = Const(parent=None,value=strip_factor,symtab=self.symtab)
        strip_factor_const3 = Const(parent=None,value=strip_factor,symtab=self.symtab)
        
        inner_assign = BinExpr(None,['times',strip_factor_const,outer_ind_var_for_inner_assign],self.symtab)

        #create new constants for the end condition and step
        outer_step_const = Const(parent=None,value=1,symtab=self.symtab)
        outer_end_const = Const(parent=None,value=(end_value//strip_factor),symtab=self.symtab)
        
        outer_step_expr = BinExpr(None,['plus',outer_ind_var,outer_step_const],self.symtab)
        outer_start_const = Const(parent=None,value=0,symtab=self.symtab)
        print('OUTER EXPRS CREATED')

        ###Creating inner loop
        #create new expressions for the inner loop
        inner_start_exp = BinExpr(None,['times',outer_ind_var_for_inner_assign,strip_factor_const],self.symtab) 
        bin_for_cond = BinExpr(None,['times',outer_ind_var_for_inner_cond,strip_factor_const2],self.symtab)
        inner_end_expr = BinExpr(None,['plus',bin_for_cond,strip_factor_const3],self.symtab)
        inner_step_expr = self.step.expr
        print('INNER EXPRS CREATED')

        inner_for = ForStat(target=self.saved_symb, op='lss', start_exp=inner_start_exp, 
            cond_expr=inner_end_expr,step_exp=inner_step_expr,body=self.body,symtab=self.symtab)
        print('INNER FOR CREATED')

        outer_for = ForStat(target=new_symb, parent=self.parent, op='lss', start_exp=outer_start_const, 
            cond_expr=outer_end_const,step_exp=outer_step_expr,body=inner_for,symtab=self.symtab)


        remainder = end_value%strip_factor
        print(remainder)
        if remainder != 0:
            rem_var_assign = Var(var=self.saved_symb, symtab=self.symtab)
            rem_var_step = Var(var=self.saved_symb, symtab=self.symtab)
            rem_var_cond = Var(var=self.saved_symb, symtab=self.symtab)
            rem_assign_exp_const = Const(parent=None,value=0,symtab=self.symtab)
            rem_step_const = Const(parent=None,value=1,symtab=self.symtab)
            original_end = self.cond.get_operands()[1].value

            rem_end_const = Const(parent=None,value=original_end,symtab=self.symtab)
            rem_step_expr = BinExpr(None,['plus',rem_var_step,rem_step_const],self.symtab)
            rem_start_const = Const(parent=None,value=0,symtab=self.symtab)
            rem_assign_exp =  BinExpr(None,['plus',rem_var_assign,rem_assign_exp_const],self.symtab)

            rem_for = ForStat(target=self.saved_symb,op='lss',start_exp=rem_var_assign,
                cond_expr=rem_end_const,step_exp=rem_step_expr,body=self.body,symtab=self.symtab)

            outer_for.remainder_for = rem_for
            rem_for.parent = outer_for
            print('REMAINDER FOR APPENDED\n')
            print(self.remainder_for)



        # rem_for = ForStat(target=self.saved_symb,parent=outer_for,op='lss',body=self.body,symtab=self.symtab)
        # rem_for.cond = self.cond
        # rem_for.step = self.step
        # outer.remainder_for = rem_for
        print('OUTER FOR CREATED')
        inner_for.parent = outer_for
        
        print('OUTER FOR INCOMINGs')
        print(outer_for)

        # #multiply body
        # remainder = end_value%strip_factor
        # print('REMAINDER %d' %remainder)
        # body_copy = self.body
        # remainder_body = StatList(self,[],self.symtab)
        # for i in range(remainder):
        #     remainder_body.append(body_copy)
        #     #remainder_body.append(self.step)
        # outer_for.unroll_remainder_statlist = remainder_body

        self.parent.replace(self, outer_for)
        print("REPLACED")
        print(outer_for.parent)



    def lower(self):
        entry_label = TYPENAMES['label']()
        exit_label = TYPENAMES['label']()
        exit_stat = EmptyStat(self.parent, symtab=self.symtab)
        exit_stat.set_label(exit_label)
        self.cond.set_label(entry_label)
        branch = BranchStat(None,self.cond.destination(),exit_label,self.symtab,negcond=True)
        loop = BranchStat(None,None, entry_label, self.symtab)
        stat_list = StatList(self.parent, [self.start_assign, self.cond, branch, self.body, self.step, loop, exit_stat,self.unroll_remainder_statlist,self.remainder_for], self.symtab)
        return self.parent.replace(self, stat_list)
        

class AssignStat(Stat):
    def __init__(self, parent=None, target=None, offset=None, expr=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.symbol = target
        try:
            self.symbol.parent = self
        except AttributeError:
            pass
        self.expr = expr
        self.expr.parent = self
        self.offset = offset
        if self.offset is not None:
            self.offset.parent = self

    def collect_uses(self):
        try:
            a = self.symbol.collect_uses()
        except AttributeError:
            a = []
        try:
            a += self.offset.collect_uses()
        except AttributeError:
            pass
        try:
            return a + self.expr.collect_uses()
        except AttributeError:
            return a

    def collect_kills(self):
        return [self.symbol]

    def lower(self):
        """Assign statements translate to a store stmt, with the symbol and a
        temporary as parameters."""

        src = self.expr.destination()
        dst = self.symbol

        stats = [self.expr]

        if self.offset:
            off = self.offset.destination()
            desttype = dst.stype
            if type(desttype) is ArrayType:  # this is always true at the moment
                desttype = desttype.basetype
            ptrreg = new_temporary(self.symtab, PointerType(desttype))
            loadptr = LoadPtrToSym(dest=ptrreg, symbol=dst, symtab=self.symtab)
            dst = new_temporary(self.symtab, PointerType(desttype))
            add = BinStat(dest=dst, op='plus', srca=ptrreg, srcb=off, symtab=self.symtab)
            stats += [self.offset, loadptr, add]

        stats += [StoreStat(dest=dst, symbol=src, symtab=self.symtab)]

        return self.parent.replace(self, StatList(children=stats, symtab=self.symtab))


class PrintStat(Stat):
    def __init__(self, parent=None, exp=None, symtab=None):
        super().__init__(parent, [exp], symtab)
        self.expr = exp

    def collect_uses(self):
        return self.expr.collect_uses()

    def lower(self):
        pc = PrintCommand(src=self.expr.destination(), symtab=self.symtab)
        stlist = StatList(children=[self.expr, pc], symtab=self.symtab)
        return self.parent.replace(self, stlist)


class PrintCommand(Stat):  # low-level node
    def __init__(self, parent=None, src=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.src = src
        if src.alloct != 'reg':
            raise RuntimeError('value not in register')

    def collect_uses(self):
        return [self.src]

    def human_repr(self):
        return 'print ' + repr(self.src)


class ReadStat(Stat):
    def __init__(self, parent=None, symtab=None):
        super().__init__(parent, [], symtab)

    def lower(self):
        tmp = new_temporary(self.symtab, TYPENAMES['int'])
        read = ReadCommand(dest=tmp, symtab=self.symtab)
        stlist = StatList(children=[read], symtab=self.symtab)
        return self.parent.replace(self, stlist)


class ReadCommand(Stat):  # low-level node
    def __init__(self, parent=None, dest=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.dest = dest
        if dest.alloct != 'reg':
            raise RuntimeError('read not to register')

    def destination(self):
        return self.dest

    def collect_uses(self):
        return []

    def collect_kills(self):
        return [self.dest]

    def human_repr(self):
        return 'read ' + repr(self.dest)


class BranchStat(Stat):  # low-level node
    def __init__(self, parent=None, cond=None, target=None, symtab=None, returns=False, negcond=False):
        """cond == None -> branch always taken.
        If negcond is True and Cond != None, the branch is taken when cond is false,
        otherwise the branch is taken when cond is true.
        If returns is True, this is a branch-and-link instruction."""
        super().__init__(parent, [], symtab)
        self.cond = cond
        self.negcond = negcond
        if not (self.cond is None) and self.cond.alloct != 'reg':
            raise RuntimeError('condition not in register')
        self.target = target
        self.returns = returns

    def collect_uses(self):
        if not (self.cond is None):
            return [self.cond]
        return []

    def is_unconditional(self):
        if self.cond is None:
            return True
        return False

    def human_repr(self):
        if self.returns:
            h = 'call '
        else:
            h = 'branch '
        if not (self.cond is None):
            c = 'on ' + ('not ' if self.negcond else '') + repr(self.cond)
        else:
            c = ''
        return h + c + ' to ' + repr(self.target)


class EmptyStat(Stat):  # low-level node
    pass

    def collect_uses(self):
        return []


class LoadPtrToSym(Stat):  # low-level node
    def __init__(self, parent=None, dest=None, symbol=None, symtab=None):
        """Loads to the 'dest' symbol the location in memory (as an absolute
        address) of 'symbol'. This instruction is used as a starting point for
        lowering nodes which need any kind of pointer arithmetic."""
        super().__init__(parent, [], symtab)
        self.symbol = symbol
        self.dest = dest
        if self.symbol.alloct == 'reg':
            raise RuntimeError('symbol not in memory')
        if self.dest.alloct != 'reg':
            raise RuntimeError('dest not to register')

    def collect_uses(self):
        return [self.symbol]

    def collect_kills(self):
        return [self.dest]

    def destination(self):
        return self.dest

    def human_repr(self):
        return repr(self.dest) + ' <- &(' + repr(self.symbol) + ')'


class StoreStat(Stat):  # low-level node
    # store the symbol to the specified destination + offset
    def __init__(self, parent=None, dest=None, symbol=None, killhint=None, symtab=None):
        """Stores the value in the 'symbol' temporary (register) to 'dest' which
        can be a symbol allocated in memory, or a temporary (symbol allocated to a
        register). In the first case, the store is done to the symbol itself; in
        the second case the dest symbol is used as a pointer to an arbitrary
        location in memory."""
        super().__init__(parent, [], symtab)
        self.symbol = symbol
        if self.symbol.alloct != 'reg':
            raise RuntimeError('store not from register')
        self.dest = dest
        self.killhint = killhint

    def collect_uses(self):
        if self.dest.alloct == 'reg':
            return [self.symbol, self.dest]
        return [self.symbol]

    def collect_kills(self):
        if self.dest.alloct == 'reg':
            if self.killhint:
                return [self.killhint]
            else:
                return []
        return [self.dest]

    def destination(self):
        return self.dest

    def human_repr(self):
        if self.dest.alloct == 'reg':
            return '[' + repr(self.dest) + '] <- ' + repr(self.symbol)
        return repr(self.dest) + ' <- ' + repr(self.symbol)


class LoadStat(Stat):  # low-level node
    def __init__(self, parent=None, dest=None, symbol=None, usehint=None, symtab=None):
        """Loads the value in symbol to dest, which must be a temporary. 'symbol'
        can be a symbol allocated in memory, or a temporary (symbol allocated to a
        register). In the first case, the value contained in the symbol itself is
        loaded; in the second case the symbol is used as a pointer to an arbitrary
        location in memory."""
        super().__init__(parent, [], symtab)
        self.symbol = symbol
        self.dest = dest
        self.usehint = usehint
        if self.dest.alloct != 'reg':
            raise RuntimeError('load not to register')

    def collect_uses(self):
        if self.usehint:
            return [self.symbol, self.usehint]
        return [self.symbol]

    def collect_kills(self):
        return [self.dest]

    def destination(self):
        return self.dest

    def human_repr(self):
        if self.symbol.alloct == 'reg':
            return repr(self.dest) + ' <- [' + repr(self.symbol) + ']'
        else:
            return repr(self.dest) + ' <- ' + repr(self.symbol)


class LoadImmStat(Stat):  # low-level node
    def __init__(self, parent=None, dest=None, val=0, symtab=None):
        super().__init__(parent, [], symtab)
        self.val = val
        self.dest = dest
        if self.dest.alloct != 'reg':
            raise RuntimeError('load not to register')

    def collect_uses(self):
        return []

    def collect_kills(self):
        return [self.dest]

    def destination(self):
        return self.dest

    def human_repr(self):
        return repr(self.dest) + ' <- ' + repr(self.val)


class BinStat(Stat):  # low-level node
    def __init__(self, parent=None, dest=None, op=None, srca=None, srcb=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.dest = dest  # symbol
        self.op = op
        self.srca = srca  # symbol
        self.srcb = srcb  # symbol
        if self.dest.alloct != 'reg':
            raise RuntimeError('binstat dest not to register')
        if self.srca.alloct != 'reg' or self.srcb.alloct != 'reg':
            raise RuntimeError('binstat src not in register')

    def collect_kills(self):
        return [self.dest]

    def collect_uses(self):
        return [self.srca, self.srcb]

    def destination(self):
        return self.dest

    def human_repr(self):
        return repr(self.dest) + ' <- ' + repr(self.srca) + ' ' + self.op + ' ' + repr(self.srcb)


class UnaryStat(Stat):  # low-level node
    def __init__(self, parent=None, dest=None, op=None, src=None, symtab=None):
        super().__init__(parent, [], symtab)
        self.dest = dest
        self.op = op
        self.src = src
        if self.dest.alloct != 'reg':
            raise RuntimeError('unarystat dest not to register')
        if self.src.alloct != 'reg':
            raise RuntimeError('unarystat src not in register')

    def collect_kills(self):
        return [self.dest]

    def collect_uses(self):
        return [self.src]

    def destination(self):
        return self.dest

    def human_repr(self):
        return repr(self.dest) + ' <- ' + self.op + ' ' + repr(self.src)


class StatList(Stat):  # low-level node
    def __init__(self, parent=None, children=None, symtab=None):
        print('StatList : new', id(self))
        super().__init__(parent, children, symtab)

    def append(self, elem):
        elem.parent = self
        print('StatList: appending', id(elem), 'of type', type(elem), 'to', id(self))
        self.children.append(elem)

    def collect_uses(self):
        u = []
        for c in self.children:
            u += c.collect_uses()
        return u

    def print_content(self):
        print('StatList', id(self), ': [', end=' ')
        for n in self.children:
            print(id(n), end=' ')
        print(']')

    def flatten(self):
        """Remove nested StatLists"""
        if type(self.parent) == StatList:
            print('Flattening', id(self), 'into', id(self.parent))
            if self.get_label():
                emptystat = EmptyStat(self, symtab=self.symtab)
                self.children.insert(0, emptystat)
                emptystat.set_label(self.get_label())
            for c in self.children:
                c.parent = self.parent
            i = self.parent.children.index(self)
            self.parent.children = self.parent.children[:i] + self.children + self.parent.children[i + 1:]
            return True
        else:
            print('Not flattening', id(self), 'into', id(self.parent), 'of type', type(self.parent))
            return False

    def destination(self):
        for i in range(-1, -len(self.children) - 1, -1):
            try:
                return self.children[i].destination()
            except Exception:
                pass
        return None


class Block(Stat):
    def __init__(self, parent=None, gl_sym=None, lc_sym=None, defs=None, body=None):
        super().__init__(parent, [], lc_sym)
        self.global_symtab = gl_sym
        self.body = body
        self.defs = defs
        self.body.parent = self
        self.defs.parent = self
        self.stackroom = 0


# DEFINITIONS

class Definition(IRNode):
    def __init__(self, parent=None, symbol=None):
        super().__init__(parent, [], None)
        self.parent = parent
        self.symbol = symbol


class FunctionDef(Definition):
    def __init__(self, parent=None, symbol=None, body=None):
        super().__init__(parent, symbol)
        self.body = body
        self.body.parent = self

    def get_global_symbols(self):
        return self.body.global_symtab.exclude([TYPENAMES['function'], TYPENAMES['label']])


class DefinitionList(IRNode):
    def __init__(self, parent=None, children=None):
        super().__init__(parent, children, None)

    def append(self, elem):
        elem.parent = self
        self.children.append(elem)


def print_stat_list(node):
    """Navigation action: print"""
    print(type(node), id(node))
    if type(node) == StatList:
        print('StatList', id(node), ': [', end=' ')
        for n in node.children:
            print(id(n), end=' ')
        print(']')
