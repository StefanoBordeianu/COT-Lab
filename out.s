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
	@ irnode 132744892069152 type <class 'ir.StatList'>
	mov r7, #0
	ldr r12, .const0
	str r7, [r12]
	mov r8, #0
	ldr r12, .const1
	str r8, [r12]
label1:
	@ emptystat
	ldr r12, .const2
	ldr r7, [r12]
	mov r8, #4
	cmp r7, r8
	movlt r7, #1
	movge r7, #0
	tst r7, r7
	beq label2
	ldr r12, .const3
	ldr r3, [r12]
	mov r4, #1
	add r5, r3, r4
	ldr r12, .const4
	str r5, [r12]
	ldr r12, .const5
	ldr r6, [r12]
	push {r0, r1, r2, r3}
	mov r0, r6
	bl __pl0_print
	pop {r0, r1, r2, r3}
	@ irnode 132744892044080 type <class 'ir.StatList'>
	ldr r12, .const6
	ldr r0, [r12]
	mov r1, #1
	add r2, r0, r1
	ldr r12, .const7
	str r2, [r12]
	@ irnode 132744892048736 type <class 'ir.StatList'>
	ldr r12, .const8
	ldr r3, [r12]
	mov r4, #1
	add r5, r3, r4
	ldr r12, .const9
	str r5, [r12]
	ldr r12, .const10
	ldr r6, [r12]
	push {r0, r1, r2, r3}
	mov r0, r6
	bl __pl0_print
	pop {r0, r1, r2, r3}
	@ irnode 132744892044080 type <class 'ir.StatList'>
	ldr r12, .const11
	ldr r0, [r12]
	mov r1, #1
	add r2, r0, r1
	ldr r12, .const12
	str r2, [r12]
	@ irnode 132744892069056 type <class 'ir.AssignStat'>
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
	.word _g_i
.const3:
	.word _g_x
.const4:
	.word _g_x
.const5:
	.word _g_x
.const6:
	.word _g_i
.const7:
	.word _g_i
.const8:
	.word _g_x
.const9:
	.word _g_x
.const10:
	.word _g_x
.const11:
	.word _g_i
.const12:
	.word _g_i
