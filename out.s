	.text
	.arch armv6
	.syntax unified
@ block
	.comm _g_x, 4
	.comm _g_i, 4
	.comm _g_y, 4
	.global __pl0_start
__pl0_start:
	push {r4, r5, r6, r7, r8, r9, r10, r11, lr}
	mov r11, sp
	sub sp, sp, #0
	@ irnode 125716642406672 type <class 'ir.StatList'>
	mov r7, #0
	ldr r12, .const0
	str r7, [r12]
	mov r8, #10
	ldr r12, .const1
	str r8, [r12]
	mov r7, #0
	ldr r12, .const2
	str r7, [r12]
label1:
	@ emptystat
	ldr r12, .const3
	ldr r8, [r12]
	mov r7, #3
	cmp r8, r7
	movlt r8, #1
	movge r8, #0
	tst r8, r8
	beq label2
	@ irnode 125716642671648 type <class 'ir.StatList'>
	ldr r12, .const4
	ldr r0, [r12]
	mov r1, #1
	add r2, r0, r1
	ldr r12, .const5
	str r2, [r12]
	ldr r12, .const6
	ldr r3, [r12]
	push {r0, r1, r2, r3}
	mov r0, r3
	bl __pl0_print
	pop {r0, r1, r2, r3}
	@ irnode 125716642675776 type <class 'ir.StatList'>
	ldr r12, .const7
	ldr r4, [r12]
	mov r5, #2
	add r6, r4, r5
	ldr r12, .const8
	str r6, [r12]
	@ irnode 125716642671648 type <class 'ir.StatList'>
	ldr r12, .const9
	ldr r0, [r12]
	mov r1, #1
	add r2, r0, r1
	ldr r12, .const10
	str r2, [r12]
	ldr r12, .const11
	ldr r3, [r12]
	push {r0, r1, r2, r3}
	mov r0, r3
	bl __pl0_print
	pop {r0, r1, r2, r3}
	@ irnode 125716642675776 type <class 'ir.StatList'>
	ldr r12, .const12
	ldr r4, [r12]
	mov r5, #2
	add r6, r4, r5
	ldr r12, .const13
	str r6, [r12]
	@ irnode 125716642407392 type <class 'ir.AssignStat'>
	b label1
label2:
	@ emptystat
	ldr r12, .const14
	ldr r0, [r12]
	mov r1, #1
	add r2, r0, r1
	ldr r12, .const15
	str r2, [r12]
	ldr r12, .const16
	ldr r3, [r12]
	push {r0, r1, r2, r3}
	mov r0, r3
	bl __pl0_print
	pop {r0, r1, r2, r3}
	mov sp, r11
	pop {r4, r5, r6, r7, r8, r9, r10, r11, lr}
	bx lr
.const0:
	.word _g_x
.const1:
	.word _g_y
.const2:
	.word _g_i
.const3:
	.word _g_i
.const4:
	.word _g_x
.const5:
	.word _g_x
.const6:
	.word _g_x
.const7:
	.word _g_i
.const8:
	.word _g_i
.const9:
	.word _g_x
.const10:
	.word _g_x
.const11:
	.word _g_x
.const12:
	.word _g_i
.const13:
	.word _g_i
.const14:
	.word _g_x
.const15:
	.word _g_x
.const16:
	.word _g_x
