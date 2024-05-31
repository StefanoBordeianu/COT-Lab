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
	@ irnode 139925114860592 type <class 'ir.StatList'>
	mov r4, #0
	ldr r12, .const0
	str r4, [r12]
	mov r5, #0
	ldr r12, .const1
	str r5, [r12]
label5:
	@ emptystat
	ldr r12, .const2
	ldr r6, [r12]
	mov r7, #1
	cmp r6, r7
	movlt r8, #1
	movge r8, #0
	tst r8, r8
	beq label6
	ldr r12, .const3
	ldr r4, [r12]
	mov r5, #5
	mul r4, r4, r5
	ldr r12, .const4
	str r4, [r12]
label1:
	@ emptystat
	ldr r12, .const5
	ldr r6, [r12]
	ldr r12, .const6
	ldr r7, [r12]
	mov r8, #5
	mul r5, r7, r8
	mov r4, #5
	add r8, r5, r4
	cmp r6, r8
	movlt r7, #1
	movge r7, #0
	tst r7, r7
	beq label2
	@ irnode 139925114789872 type <class 'ir.StatList'>
	ldr r12, .const7
	ldr r0, [r12]
	mov r1, #1
	add r2, r0, r1
	ldr r12, .const8
	str r2, [r12]
	ldr r12, .const9
	ldr r3, [r12]
	push {r0, r1, r2, r3}
	mov r0, r3
	bl __pl0_print
	pop {r0, r1, r2, r3}
	ldr r12, .const10
	ldr r8, [r12]
	mov r5, #1
	add r4, r8, r5
	ldr r12, .const11
	str r4, [r12]
	b label1
label2:
	@ emptystat
	ldr r12, .const12
	ldr r6, [r12]
	mov r7, #1
	add r8, r6, r7
	ldr r12, .const13
	str r8, [r12]
	b label5
label6:
	@ emptystat
	ldr r12, .const14
	ldr r5, [r12]
	ldr r12, .const15
	str r5, [r12]
label3:
	@ emptystat
	ldr r12, .const16
	ldr r4, [r12]
	mov r6, #8
	cmp r4, r6
	movlt r7, #1
	movge r7, #0
	tst r7, r7
	beq label4
	ldr r12, .const17
	ldr r0, [r12]
	mov r1, #1
	add r2, r0, r1
	ldr r12, .const18
	str r2, [r12]
	ldr r12, .const19
	ldr r3, [r12]
	push {r0, r1, r2, r3}
	mov r0, r3
	bl __pl0_print
	pop {r0, r1, r2, r3}
	ldr r12, .const20
	ldr r2, [r12]
	mov r0, #1
	add r8, r2, r0
	ldr r12, .const21
	str r8, [r12]
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
.const14:
	.word _g_i
.const15:
	.word _g_i
.const16:
	.word _g_i
.const17:
	.word _g_x
.const18:
	.word _g_x
.const19:
	.word _g_i
.const20:
	.word _g_i
.const21:
	.word _g_i
