# eee_bench 改写样例分析

- 生成时间：`2026-04-07T10:10:05Z`
- ready 包：`ready/eee_bench/run_merged_eee_bench_1000_2860_dedup`
- 自动结果分布：`pass=667 / review=285 / reject=4`

## Pass 样本分析

- pass 样本数：`667`
- 改写策略分布：`blank_open=383, drop_image_index=57, keep_open=376, split_open=140`

### Pass 案例 1：`prob_0077989c1a069e785bfb21c3`

- source_problem_id：`1`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_0077989c1a069e785bfb21c3_primary_roi.png)

**原题**

The characteristic equation of the flip-flop shown in figure is:

**改写**

What is the characteristic equation of the flip-flop shown in the figure?

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 2：`prob_012e7649abcca0cbdd762b2d`

- source_problem_id：`798`
- rewrite_strategy：`keep_open`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_012e7649abcca0cbdd762b2d_primary_roi.png)

**原题**

Find the transfer function \( \frac{Y(s)}{X(s)} \) of the system given shown in <image>.

**改写**

Find the transfer function \( \frac{Y(s)}{X(s)} \) of the system shown in the image.

**分析**

该样本自动结果为 `pass`，改写策略是 `keep_open`。 改写基本保持开放题结构，主要做措辞与格式规范化。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 3：`prob_56cec3b154ce0194f756f437`

- source_problem_id：`81`
- rewrite_strategy：`split_open`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_56cec3b154ce0194f756f437_primary_roi.png)

**原题**

It is desired to find a three-tap causal filter which gives zero signal as an output to an input of the form 

\( x[n] = c_1 \exp \left(- \frac{j \pi n}{2}\right) + c_2 \exp \left(\frac{j \pi n}{2}\right) \) 

where \( c_1 \) and \( c_2 \) are arbitrary real numbers. The desired three-tap filter is given by 

\( h[0] = 1, \, h[1] = a, \, h[2] = b \) 

and 

\( h[n] = 0 \) for \( n < 0 \) or \( n > 2 \).

What are the values of the filter taps \( a \) and \( b \) if the output is \( y[n] = 0 \) for all \( n \), when \( x[n] \) is as given above?

**改写**

It is desired to find a three-tap causal filter which gives zero signal as an output to an input of the form

\( x[n] = c_1 \exp\left(-\frac{j\pi n}{2}\right) + c_2 \exp\left(\frac{j\pi n}{2}\right) \)

where \( c_1 \) and \( c_2 \) are arbitrary real numbers. The desired three-tap filter is given by

\( h[0] = 1,\; h[1] = a,\; h[2] = b \)

and \( h[n] = 0 \) for \( n < 0 \) or \( n > 2 \).

If the output is \( y[n] = 0 \) for all \( n \) when \( x[n] \) is as given above, what is the value of the filter tap \( a \)?

**分析**

该样本自动结果为 `pass`，改写策略是 `split_open`。 虽然经过拆分式改写，但仍通过了自动检查，说明题意保持较稳定。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 4：`prob_008548426bf83df9dc26bba9`

- source_problem_id：`82`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_008548426bf83df9dc26bba9_primary_roi.png)

**原题**

Given that the waveforms of the signals \( x_1(t) \) and \( x_2(t) \) are as shown in the <image>, the expression for \( x(t) = x_1(t) * x_2(t) \) is [ ].

**改写**

Given that the waveforms of the signals \(x_1(t)\) and \(x_2(t)\) are as shown in the image, what is the expression for \(x(t)=x_1(t)*x_2(t)\)?

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

### Pass 案例 5：`prob_00e561055d377d1bbe1a66b7`

- source_problem_id：`63`
- rewrite_strategy：`blank_open`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_00e561055d377d1bbe1a66b7_primary_roi.png)

**原题**

The figure shows the artificial mechanical characteristics of a separately excited DC motor at different voltages, where curve 1 corresponds to the mechanical characteristic at \( U = U_N \); curves 2 and 3 correspond to the artificial mechanical characteristics at \( U = U_1 \) and \( U = U_2 \), respectively. The relationship between \( U_N \), \( U_1 \), and \( U_2 \) is ________.

**改写**

Based on the figure, what is the relationship among \( U_N \), \( U_1 \), and \( U_2 \)? Answer by ordering them from largest to smallest.

**分析**

该样本自动结果为 `pass`，改写策略是 `blank_open`。 改写把原始素材整理成开放问答形式，但没有引入新的审查风险信号。 该 ready 包本身来自更严格的 filtered-safe 选择，因此这类样本更接近“稳定可直接通过”的代表。

## Review 原因分析

| review reason | count |
| --- | --- |
| split_variant_needs_review | 92 |
| visual_evidence_uncertain | 49 |
| alignment_requires_review | 37 |
| pure_image_choice_task | 22 |
| split_open_rewrite | 21 |
| rewrite_unusable | 21 |
| split_variant_incomplete | 15 |
| metadata_inconsistency | 14 |

### Review 案例 1：`prob_05f4a6378d1d9df87dc4fcad`

- source_problem_id：`95`
- review reasons：`split_variant_needs_review`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_05f4a6378d1d9df87dc4fcad_primary_roi.png)

**原题**

Given the block diagram of a closed-loop discrete control system as shown in <image>, determine \( Y(s) \) and \( Y(z) \).

**改写**

Given the block diagram of the closed-loop discrete control system shown in the image, determine the expression for \(Y(s)\).

**分析**

该样本进入 `review` 的主因是 `split_variant_needs_review`，说明自动链路在这个风险点上无法直接放行。

### Review 案例 2：`prob_0067da74081eb9418004a892`

- source_problem_id：`812`
- review reasons：`pure_image_option_selection, rewrite_unusable, visual_evidence_uncertain`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_0067da74081eb9418004a892_primary_roi.png)

**原题**

Figure shows the extended view of a 2-pole DC machine with 10 armature conductors. Normal brush positions are shown by A and B, placed at the interpolar axis. If the brushes are now shifted, in the direction of rotation, to \( A' \) and \( B' \) as shown, the voltage waveform \( V_{A'B'} \) will resemble:

**改写**

Figure shows the extended view of a 2-pole DC machine with 10 armature conductors. Normal brush positions are shown by A and B, placed at the interpolar axis. If the brushes are now shifted, in the direction of rotation, to A' and B' as shown, the voltage waveform V_{A'B'} will resemble:

**分析**

该样本同时触发了多个 review 原因：`pure_image_option_selection, rewrite_unusable, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 3：`prob_025e33dd43adf3ab920b3699`

- source_problem_id：`58`
- review reasons：`alignment_requires_review, metadata_reference_inconsistent, visual_evidence_uncertain`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/images/prob_025e33dd43adf3ab920b3699_primary.png)

**原题**

Consider a power system shown in the <image>. Given that \( V_{S1} = V_{S2} = 1 + j0 \, \text{p.u} \); The positive sequence impedance are \( Z_{S1} = Z_{S2} = 0.001 + j0.01 \, \text{p.u} \) and \( Z_L = 0.006 + j0.06 \, \text{p.u} \). 3-phase Base MVA = 100, voltage base = 400 kV (Line to Line), Nominal system frequency = 50 Hz. The reference voltage for phase 'a' is defined as \( v(t) = V_m \cos(\omega t) \). A symmetrical three-phase fault occurs at the center of the line, i.e., point 'F' at time \( t_0 \). The positive sequence impedance from source S1 to point 'F' equals \( 0.004 + j0.04 \, \text{p.u} \). The waveform corresponding to phase 'a' fault current from bus X reveals that decaying d.c. offset current is negative and in magnitude at its maximum initial value. Assume that the negative sequence impedances are equal to positive sequence impedance and the zero sequence impedances are three times positive sequence impedances.
The instant (\( t_0 \)) of the fault will be ________

**改写**

Consider a power system shown in the image. Given that \( V_{S1} = V_{S2} = 1 + j0 \, \text{p.u} \); the positive-sequence impedances are \( Z_{S1} = Z_{S2} = 0.001 + j0.01 \, \text{p.u} \) and \( Z_L = 0.006 + j0.06 \, \text{p.u} \). 3-phase base MVA = 100, voltage base = 400 kV (line-to-line), nominal system frequency = 50 Hz. The reference voltage for phase 'a' is defined as \( v(t) = V_m \cos(\omega t) \). A symmetrical three-phase fault occurs at the center of the line, i.e., point 'F', at time \( t_0 \). The positive-sequence impedance from source S1 to point 'F' equals \( 0.004 + j0.04 \, \text{p.u} \). The waveform corresponding to phase 'a' fault current from bus X reveals that the decaying d.c. offset current is negative and is at its maximum initial magnitude. Assume that the negative-sequence impedances are equal to the positive-sequence impedance and the zero-sequence impedances are three times the positive-sequence impedances.
The instant \( t_0 \) of the fault is ________.

**分析**

该样本同时触发了多个 review 原因：`alignment_requires_review, metadata_reference_inconsistent, visual_evidence_uncertain`，属于复合风险案例，不适合直接自动放行。

### Review 案例 4：`prob_060c0dd181c350bba6b3b6e4`

- source_problem_id：`535`
- review reasons：`answer_option_label_only, pure_image_choice_task, rewrite_unusable`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_060c0dd181c350bba6b3b6e4_primary_roi.png)

**原题**

Assuming the diodes \( D_1 \) and \( D_2 \) of the circuit shown in the <image> to be ideal, the transfer characteristics of the circuit will be

**改写**

Assuming the diodes \(D_1\) and \(D_2\) of the circuit shown in the image to be ideal, the transfer characteristics of the circuit will be

**分析**

该样本同时触发了多个 review 原因：`answer_option_label_only, pure_image_choice_task, rewrite_unusable`，属于复合风险案例，不适合直接自动放行。

### Review 案例 5：`prob_005f1e6430fb74f3ea7f0b91`

- source_problem_id：`222`
- review reasons：`minor_text_legibility, split_open_rewrite`
- 图片：![](../ready/eee_bench/run_merged_eee_bench_1000_2860_dedup/datasets/eee_bench/artifacts/crops/prob_005f1e6430fb74f3ea7f0b91_primary_roi.png)

**原题**

The voltage across the capacitor, as shown in the figure, is expressed as \(v_c(t) = A_1\sin(\omega_1t - \theta_1) + A_2\sin(\omega_2t - \theta_2)\). The values of \(A_1\) and \(A_2\) respectively, are _______.

**改写**

The voltage across the capacitor, as shown in the figure, is expressed as \(v_c(t) = A_1\sin(\omega_1 t - \theta_1) + A_2\sin(\omega_2 t - \theta_2)\). What is the value of \(A_1\)?

**分析**

该样本同时触发了多个 review 原因：`minor_text_legibility, split_open_rewrite`，属于复合风险案例，不适合直接自动放行。

## 小结

当前数据集同时存在稳定通过样本与需人工复核样本（pass=667, review=285, reject=4）；review 主要集中在 `split_variant_needs_review` 一类问题。
