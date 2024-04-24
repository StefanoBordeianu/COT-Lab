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
	@ irnode 139642234706704 type <class 'ir.StatList'>
	mov r0, #1
	ldr r12, .const0
	str r0, [r12]
	mov r1, #0
	ldr r12, .const1
	str r1, [r12]
label1:
	@ emptystat
	ldr r12, .const2
	ldr r2, [r12]
	mov r3, #10
	cmp r2, r3
	movlt r4, #1
	movge r4, #0
	tst r4, r4
	beq label2
	ldr r12, .const3
	ldr r5, [r12]
	mov r6, #1
	add r7, r5, r6
	ldr r12, .const4
	str r7, [r12]
	ldr r12, .const5
	ldr r8, [r12]
	push {r0, r1, r2, r3}
	mov r0, r8
	bl __pl0_print
	pop {r0, r1, r2, r3}
	ldr r12, .const6
	ldr r0, [r12]
	mov r1, #1
	add r0, r0, r1
	ldr r12, .const7
	str r0, [r12]
	b label1
label2:
	@ emptystat
	ldr r12, .const8
	ldr r2, [r12]
	push {r0, r1, r2, r3}
	mov r0, r2
	bl __pl0_print
	pop {r0, r1, r2, r3}
	ldr r12, .const9
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
	.word _g_i
