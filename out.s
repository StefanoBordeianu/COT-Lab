	.text
	.arch armv6
	.syntax unified
@ block
	.comm _g_x, 4
	.comm _g_i, 4
	.global __pl0_start
__pl0_start:
	push {r4, r5, r6, r7, r8, r9, r10, r11, lr}
	mov r11, sp
	sub sp, sp, #0
	@ irnode 140556240935552 type <class 'ir.StatList'>
	mov r0, #1
	ldr r12, .const0
	str r0, [r12]
	@ irnode 140556239136912 type <class 'ir.AssignStat'>
label1:
	@ emptystat
	ldr r12, .const1
	ldr r1, [r12]
	mov r2, #10
	cmp r1, r2
	movlt r3, #1
	movge r3, #0
	tst r3, r3
	beq label2
	ldr r12, .const2
	ldr r4, [r12]
	mov r5, #1
	add r6, r4, r5
	ldr r12, .const3
	str r6, [r12]
	ldr r12, .const4
	ldr r7, [r12]
	mov r8, #1
	add r0, r7, r8
	ldr r12, .const5
	str r0, [r12]
	b label1
label2:
	@ emptystat
	mov sp, r11
	pop {r4, r5, r6, r7, r8, r9, r10, r11, lr}
	bx lr
.const0:
	.word _g_x
.const1:
	.word _g_i
.const2:
	.word _g_x
.const3:
	.word _g_x
.const4:
	.word _g_i
.const5:
	.word _g_i
