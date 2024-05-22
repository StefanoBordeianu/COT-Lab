	.text
	.arch armv6
	.syntax unified
@ block
	.comm _g_x, 4
	.comm _g_i, 4
	.comm _g_tmp_variable_for_strip_mining, 4
	.global __pl0_start
__pl0_start:
	push {r4, r5, r6, r7, r8, r9, r10, r11, lr}
	mov r11, sp
	sub sp, sp, #0
	@ irnode 140422647882432 type <class 'ir.StatList'>
	mov r0, #0
	ldr r12, .const0
	str r0, [r12]
	mov r1, #0
	ldr r12, .const1
	str r1, [r12]
label3:
	@ emptystat
	ldr r12, .const2
	ldr r2, [r12]
	mov r3, #2
	cmp r2, r3
	movlt r4, #1
	movge r4, #0
	tst r4, r4
	beq label4
	ldr r12, .const3
	ldr r5, [r12]
	mov r6, #4
	mul r7, r5, r6
	ldr r12, .const4
	str r7, [r12]
label1:
	@ emptystat
	ldr r12, .const5
	ldr r8, [r12]
	ldr r12, .const6
	ldr r0, [r12]
	mov r1, #4
	mul r0, r0, r1
	mov r2, #4
	add r3, r0, r2
	cmp r8, r3
	movlt r4, #1
	movge r4, #0
	tst r4, r4
	beq label2
	ldr r12, .const7
	ldr r5, [r12]
	mov r6, #1
	add r7, r5, r6
	ldr r12, .const8
	str r7, [r12]
	ldr r12, .const9
	ldr r3, [r12]
	push {r0, r1, r2, r3}
	mov r0, r3
	bl __pl0_print
	pop {r0, r1, r2, r3}
	ldr r12, .const10
	ldr r8, [r12]
	mov r1, #1
	add r0, r8, r1
	ldr r12, .const11
	str r0, [r12]
	b label1
label2:
	@ emptystat
	ldr r12, .const12
	ldr r2, [r12]
	mov r1, #1
	add r4, r2, r1
	ldr r12, .const13
	str r4, [r12]
	b label3
label4:
	@ emptystat
	mov sp, r11
	pop {r4, r5, r6, r7, r8, r9, r10, r11, lr}
	bx lr
.const0:
	.word _g_x
.const1:
	.word _g_tmp_variable_for_strip_mining
.const2:
	.word _g_tmp_variable_for_strip_mining
.const3:
	.word _g_tmp_variable_for_strip_mining
.const4:
	.word _g_i
.const5:
	.word _g_i
.const6:
	.word _g_tmp_variable_for_strip_mining
.const7:
	.word _g_x
.const8:
	.word _g_x
.const9:
	.word _g_i
.const10:
	.word _g_i
.const11:
	.word _g_i
.const12:
	.word _g_tmp_variable_for_strip_mining
.const13:
	.word _g_tmp_variable_for_strip_mining
