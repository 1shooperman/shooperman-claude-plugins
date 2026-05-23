---
name: onboard-user
description: Use this skill when the user wants to set up their athlete profile, run intake for the first time, or update their USER_CONTEXT.md for the coaching system.
user-invocable: true
allowed-tools: [Write]
---

# onboard

Invocation: `/onboard`

Collects the information needed to build or refresh `USER_CONTEXT.md` for the coaching panel. Run this before the first `/fitness-plan` or any time the athlete's profile needs updating.

Work through questions **one group at a time**. Wait for the user's answers before moving to the next group. Do not ask all groups at once.

---

## Group 1 — Who You Are

Ask these together:

> **Let's start with the basics.**
>
> 1. What's your age or birth year?
> 2. Height and current weight?
> 3. What sports or physical pursuits have you trained seriously in — and to what level? Include anything from youth through now.
> 4. How would you describe your current activity level? (e.g., sedentary, lightly active, training 3x/week, etc.)

*Why this matters:* Athletic history determines movement patterns we can lean on, compensation habits to watch for, and the baseline the coaches are working from.

---

## Group 2 — How You Think and Work

Ask these together:

> **A few questions about how you make decisions and what you're working with.**
>
> 1. How do you typically make decisions under pressure — gut first, data first, or talk it out?
> 2. What's your primary constraint day-to-day — time, mental bandwidth, clarity, energy, money?
> 3. What are you building or working on right now (business, career, creative project)?
> 4. Who are you accountable to?
> 5. What's your 12-month revenue or impact goal?
> 6. Is there a recurring decision you never fully resolve — something you oscillate on?
> 7. What's one commitment you keep avoiding making?

*Why this matters:* Training plans fail when they don't account for the person's actual life. Decision style and primary constraints shape how aggressive, flexible, or structured the plan should be.

---

## Group 3 — Medical & Physiological Baseline

Ask these together:

> **Now for some health and physiology context.**
>
> 1. Do you know your blood type?
> 2. Any known lung, cardiac, or respiratory history? Do you know your resting SPO2?
> 3. Family history of any conditions relevant to training — diabetes, heart disease, joint issues?
> 4. How would you describe your body composition type? (ectomorph / mesomorph / endomorph, or just describe it in your own words)
> 5. Do you run hot or cold? Any known issues with hydration or electrolyte needs?
> 6. Any recurring tightness or mobility limitations? (e.g., hamstrings, hip flexors, shoulders)

*Why this matters:* These flags directly influence intensity ceilings, supplementation, recovery windows, and how the longevity and cardio coaches will frame their recommendations.

---

## Group 4 — Injuries and Asymmetries

Ask these together:

> **Tell me about your injury history.**
>
> 1. Any current or chronic injuries? Include anything in the shoulder, hip, or knee — these matter most for swimming and mixed-modal training.
> 2. Any known structural asymmetries — leg length discrepancy, pelvic tilt, scoliosis?
> 3. Dominant hand and foot?

*Why this matters:* The swim and strength coaches will build around these. Asymmetries caught here prevent compounding them in the plan.

---

## Group 5 — High-Value Measurements

> **A few measurements. Self-measured is fine — just note the margin of error.**
>
> 1. **Inseam** — bare floor to crotch, standing straight. Pins your true leg length for gait and any future bike fit work.
> 2. **Wingspan** — fingertip to fingertip, arms level. Cross-checks your ape index.
> 3. **Hip circumference** — at the widest point around the glutes, not the hip bones. Used for waist-to-hip ratio.
> 4. **Resting heart rate** — first thing in the morning before you move. Anchors MAF and recovery zone targets.

---

## Group 6 — Moderate-Value Measurements

> **A few more if you have them (or can grab them now):**
>
> 1. **Seated height** — sitting straight on the floor, floor to crown of head. Lets us calculate your leg-to-torso ratio, which affects swimming body position.
> 2. **Calf circumference** — at the widest point.
> 3. **Thigh circumference** — at the widest, roughly 6 inches below the crotch.

---

## Group 7 — Contextual Details

> **Last few, lower stakes but useful:**
>
> 1. Foot arch type — flat, neutral, or high arch?
> 2. Shoe size?
> 3. Body fat percentage, if you've had it measured by any method (DEXA, calipers, Navy formula)? If not, skip it.

---

## Group 8 — Goals and Coaching Preferences

> **Finally — what are we actually trying to do?**
>
> 1. What's the primary goal you want the coaching panel to build toward? Be specific: distance, time, lift, race, date.
> 2. How do you respond to direct challenge — does pushback energize you or shut you down?
> 3. Is there a domain (e.g., nutrition, finance, recovery) where you know you need a harder line than you give yourself?
> 4. What have previous coaches or training plans gotten wrong about you?

*Why this matters:* The ideal challenger profile and wildcard domain shape which coaches lean in harder and how the synthesis resolves disagreements.

---

## Output

After all groups are complete:

1. Write or overwrite `~/.cache/fitness-coach/USER_CONTEXT.md` with a structured athlete profile derived from the answers.
2. Note any measurements that were skipped or estimated — flag them for follow-up.
3. Confirm to the user: "Profile saved. You're ready to run `/plan`."
