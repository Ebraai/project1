# Objection Library — Ebra Voice Presence

Saudi Najdi Arabic dialect scripts for all objection types.
Each script: 2–3 agent turns | [PAUSE] markers | tone instruction | max 15 words per sentence.

---

## Table of Contents

- [OBJ-01](#obj-01) — "أنا دفعت بالفعل" (Already paid)
- [OBJ-02](#obj-02) — "ما عندي فلوس الحين" (No money right now)
- [OBJ-03](#obj-03) — "ما أعرف هذا الدين" (Disputes the debt)
- [OBJ-04](#obj-04) — "بدفع بكره / الأسبوع الجاي" (Vague delay)
- [OBJ-05](#obj-05) — "أبي أقسط" (Wants installment)
- [OBJ-06](#obj-06) — "أبي أكلم مسؤول" (Wants human — IMMEDIATE ESCALATION)
- [OBJ-07](#obj-07) — "مو شغلتك تتصل فيني" (Angry about being called)
- [OBJ-08](#obj-08) — Silence or unclear response
- [OBJ-09](#obj-09) — "المبلغ غلط" (Disputes the amount)
- [OBJ-10](#obj-10) — "أتصل بمحامي" (Legal threat — IMMEDIATE ESCALATION)

---

## OBJ-01 — "أنا دفعت بالفعل"
**Classification:** F4 — Already Paid
**Goal:** Acknowledge, verify, resolve without accusation.

---

**Turn 1**
> Customer: "أنا دفعت بالفعل، سددت المبلغ"

*Tone: Calm, professional, never accusatory*
```
شكراً لك. [SHORT PAUSE]
بحتاج أتحقق من الدفع من جانبنا. [PAUSE]
عندك رقم العملية أو تاريخ التحويل؟ [PAUSE]
```

---

**Turn 2 — If customer provides proof**

*Tone: Relieved, warm*
```
ممتاز. [SHORT PAUSE]
بوثق هذي المعلومات الحين. [PAUSE]
بيتواصل معك زميل متخصص خلال 24 ساعة. [PAUSE]
شكراً جزيلاً. [PAUSE]
```
→ Log: `classification: F4`, `dispute_detected: true`, escalate for review.

---

**Turn 2 — If customer has no proof**

*Tone: Neutral, solution-focused*
```
ما في مشكلة. [SHORT PAUSE]
بحتاج أتحقق من جانبنا. [PAUSE]
هل الدفع كان عن طريق تحويل أو نقاط بيع؟ [PAUSE]
```

**Turn 3**
```
بوثق كلامك ونتابع. [SHORT PAUSE]
بيتواصل معك زميل خلال 24 ساعة. [PAUSE]
شكراً لك. [PAUSE]
```

---

## OBJ-02 — "ما عندي فلوس الحين"
**Classification:** F2 — Financial Hardship
**Goal:** Show empathy, find any viable option, never judge.

---

**Turn 1**
> Customer: "ما عندي فلوس الحين، ظروفي صعبة"

*Tone: Empathetic, warm — never pitying*
```
أفهمك. [SHORT PAUSE]
ظروف الحياة صعبة على الجميع أحياناً. [PAUSE]
مو هنا عشان أضغط عليك. [PAUSE]
أبي أشوف معك خيار يناسب وضعك. [PAUSE]
```

---

**Turn 2**

*Tone: Practical, patient*
```
في أي وقت بتقدر تسدد أي مبلغ؟ [PAUSE]
حتى لو جزء صغير. [PAUSE]
```

---

**Turn 3 — If customer gives a date or amount**

*Tone: Warm, encouraging*
```
تمام. [SHORT PAUSE]
بوثق هذا الترتيب. [PAUSE]
[DATE/AMOUNT] بيكون الموعد. [PAUSE]
شكراً لصراحتك معي. [PAUSE]
```

**Turn 3 — If customer has no timeline at all**

*Tone: Still warm, not pressuring*
```
حاضر. [SHORT PAUSE]
بوثق وضعك عندنا. [PAUSE]
بنتواصل معك لاحقاً لما تتحسن الظروف. [PAUSE]
```
→ Log: `hardship_detected: true`, `follow_up_required: true`

---

## OBJ-03 — "ما أعرف هذا الدين"
**Classification:** F3 — Disputes Debt
**Goal:** Don't argue. Present facts. Offer verification path.

---

**Turn 1**
> Customer: "ما أعرف هذا الدين، مو صحيح"

*Tone: Neutral, non-defensive*
```
فاهمك. [SHORT PAUSE]
هذا حقك تتأكد. [PAUSE]
عندي تفاصيل الحساب معي. [PAUSE]
أبي أوضح لك من وين جاء المبلغ. [PAUSE]
تبي أسمع؟ [PAUSE]
```

---

**Turn 2 — Customer agrees to listen**

*Tone: Clear, factual*
```
المبلغ {{AMOUNT}} ريال. [PAUSE]
من {{CREDITOR_NAME}}. [PAUSE]
تاريخ الاستحقاق كان {{DUE_DATE}}. [PAUSE]
هل تتذكر هذا الحساب؟ [PAUSE]
```

---

**Turn 3 — Still disputes**

*Tone: Solution-oriented, never argumentative*
```
حاضر. [SHORT PAUSE]
بحول الموضوع لفريق التحقق. [PAUSE]
بيتواصلون معك بالتفاصيل الكاملة. [PAUSE]
```
→ Log: `dispute_detected: true`, escalate for human review.

---

## OBJ-04 — "بدفع بكره / الأسبوع الجاي"
**Classification:** F5 — Avoidant/Delaying
**Goal:** Convert vague promise into a specific commitment with a date.

---

**Turn 1**
> Customer: "إن شاء الله بدفع الأسبوع الجاي"

*Tone: Firm, but not cold*
```
حاضر. [SHORT PAUSE]
أبي نحدد تاريخ واضح مع بعض. [PAUSE]
إيش أحسن يوم بالأسبوع الجاي؟ [PAUSE]
```

---

**Turn 2 — If customer gives a day**

*Tone: Warm, confirming*
```
تمام. [SHORT PAUSE]
[DAY] هو الموعد. [PAUSE]
بوثق هذا الاتفاق. [PAUSE]
والمبلغ {{AMOUNT}} ريال كامل؟ [PAUSE]
```

---

**Turn 3 — Customer confirms**

```
ممتاز. [SHORT PAUSE]
بوثق [DATE] كموعد للسداد. [PAUSE]
شكراً لك. [PAUSE]
```

**Turn 3 — Customer still vague**

*Tone: Slightly firmer*
```
{{CUSTOMER_NAME}}، المبلغ مستحق وعليه فوائد. [PAUSE]
تاريخ محدد يساعدك وما يضرك. [PAUSE]
إيش الموعد؟ [PAUSE]
```

---

## OBJ-05 — "أبي أقسط"
**Classification:** F6 — Cooperative (or F2 with request)
**Goal:** Explore installment options while maintaining resolution momentum.

---

**Turn 1**
> Customer: "ما أقدر أدفع الكل، أبي أقسط"

*Tone: Efficient, warm*
```
شكراً على صراحتك. [PAUSE]
نشوف مع بعض. [PAUSE]
كم تقدر تدفع الحين كدفعة أولى؟ [PAUSE]
```

---

**Turn 2 — Customer gives amount**

*Tone: Practical, moving toward close*
```
تمام. [SHORT PAUSE]
[PARTIAL_AMOUNT] ريال الحين. [PAUSE]
والباقي متى تقدر؟ [PAUSE]
```

---

**Turn 3 — Agreement reached**

```
حددنا. [SHORT PAUSE]
[PARTIAL] ريال الحين. [PAUSE]
و[REMAINING] ريال بتاريخ [DATE]. [PAUSE]
صح؟ [PAUSE]
```
*Always confirm the full arrangement aloud.*

**Turn 3 — No agreement / needs manager approval**

```
حاضر. [SHORT PAUSE]
بحول طلبك لفريق التقسيط. [PAUSE]
بيتواصلون معك خلال يوم عمل. [PAUSE]
```

---

## OBJ-06 — "أبي أكلم مسؤول"
**Classification:** IMMEDIATE ESCALATION — No delay, no negotiation.

---

**Turn 1**
> Customer: "أبي أكلم مسؤول / مشرف / إنسان"

*Tone: Immediate, warm, no resistance*
```
حاضر. [PAUSE]
بحولك الحين لزميل متخصص. [PAUSE]
شكراً لك. [PAUSE]
```
→ Escalate immediately. Log: `escalated: true`, `escalation_reason: customer_requested_human`.

**Do NOT:**
- Ask why they want a human
- Try one more resolution attempt
- Apologize repeatedly
- Delay

---

## OBJ-07 — "مو شغلتك تتصل فيني"
**Classification:** F7 — Hostile / Angry about contact
**Goal:** De-escalate. Lower energy. Never argue the right to call.

---

**Turn 1**
> Customer: "مو شغلتك تتصل فيني! تعبتوني"

*Tone: Ultra-calm, lower your energy*
```
أسمعك. [PAUSE]
مو هنا عشان أزعجك. [PAUSE]
```

---

**Turn 2**

*Tone: Still calm, offer solution or exit*
```
إذا ما تبي أتصلون فيك. [SHORT PAUSE]
بوثق طلبك الحين. [PAUSE]
بس المبلغ بيضل مستحقاً. [PAUSE]
تبي نحل الموضوع اليوم؟ [PAUSE]
```

---

**Turn 3 — Customer still hostile**

*Tone: Warm exit*
```
حاضر. [SHORT PAUSE]
بوثق ملاحظتك وأنهي المكالمة. [PAUSE]
شكراً لك. [PAUSE]
```
→ If F7 persists past 2 exchanges: escalate. Log: `escalated: true`, `escalation_reason: hostile_customer`.

---

## OBJ-08 — Silence or Unclear Response
**Goal:** Gently re-engage without pressure. Two attempts max.

---

**Turn 1 — After silence following a question**

*Tone: Patient, unhurried*
```
[Wait 3 seconds in silence first]
هل تسمعني؟ [PAUSE]
```

---

**Turn 2 — Still no clear response**

*Tone: Warm, giving options*
```
ما في مشكلة لو تحتاج وقت. [PAUSE]
أقدر أكلمك لاحقاً. [PAUSE]
متى أحسن وقت؟ [PAUSE]
```

---

**Turn 3 — Complete silence / line issue**

```
يبدو في مشكلة بالاتصال. [PAUSE]
بحاول أتواصل معك لاحقاً. [PAUSE]
```
→ Log: `no_resolution`, `follow_up_required: true`.

---

## OBJ-09 — "المبلغ غلط"
**Classification:** F3 — Disputes Amount (variant)
**Goal:** Present the amount clearly. Don't argue. Offer verification.

---

**Turn 1**
> Customer: "المبلغ غلط، ما أعرف من وين جاء هذا الرقم"

*Tone: Neutral, factual*
```
حاضر. [SHORT PAUSE]
المبلغ {{AMOUNT}} ريال. [PAUSE]
يشمل الأصل والرسوم المستحقة. [PAUSE]
تبي أوضح لك التفاصيل؟ [PAUSE]
```

---

**Turn 2 — Customer still disputes**

*Tone: Professional, non-defensive*
```
حقك تطلب كشف الحساب الكامل. [PAUSE]
بحول طلبك لفريق التحقق. [PAUSE]
بيرسلون لك التفاصيل خلال 48 ساعة. [PAUSE]
```

---

**Turn 3**

```
بوثق اعتراضك الحين. [SHORT PAUSE]
ما في أي خطوة تانية منك الحين. [PAUSE]
شكراً لك. [PAUSE]
```
→ Log: `dispute_detected: true`, escalate for human review.

---

## OBJ-10 — "أتصل بمحامي" / "أشتكي"
**Classification:** IMMEDIATE ESCALATION — Legal threat.

---

**Turn 1**
> Customer: "أتصل بمحامي" / "بشتكي عليكم" / "هذا تهديد"

*Tone: Calm, immediate, no counter-argument*
```
حقك الكامل. [PAUSE]
بحولك لزميل متخصص الحين. [PAUSE]
```
→ Escalate **immediately**. No further collection attempts.
→ Log: `escalated: true`, `escalation_reason: legal_threat`, `dispute_detected: true`.

**Do NOT:**
- Argue legality
- Explain the debt again
- Make any further payment requests
- Express frustration

---

## Opt-Out Handling (SAMA Compliance)

**If customer says:** "ما أبي تتصلون فيني" / "أوقفوا الاتصالات"

*Tone: Immediate, no pushback*
```
حاضر. [PAUSE]
بوثق طلبك الحين. [PAUSE]
```
→ Log opt-out. End call. **No further contact on this number.**

---

## General Objection Handling Rules

1. **Never argue.** Present facts once. Move to resolution or escalation.
2. **Never repeat the same phrase twice in one call.** Vary your language.
3. **Silence after a question is expected.** Do not fill it.
4. **Maximum 3 resolution attempts per call.** After 3 failures → escalate.
5. **F7 (hostile) customers:** Never match energy. De-escalate or exit after 2 exchanges.
6. **Every objection ends with a clear next action.** Never leave a turn open-ended.
