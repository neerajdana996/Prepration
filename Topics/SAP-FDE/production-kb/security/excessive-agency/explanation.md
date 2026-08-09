# Excessive agency

## What it is
The LLM stops being a text generator and becomes an **actor**: you give it *tools* (functions
it can call — refund a customer, delete a row, send an email). **Excessive agency** is when the
agent has **more power than the task needs** and can take **harmful or irreversible actions on its
own**. OWASP calls it **LLM06:2025 Excessive Agency**, the risk of granting an LLM too much
functionality, permission, or autonomy.

![too many tools, no gate](images/excessive-agency.svg)

## How it happens (OWASP's three root causes)
- **Excessive functionality** — the agent is handed *too many / too-powerful tools*. A support bot
  gets a `delete_account` tool it never needed just because the tool library was wired in wholesale.
- **Excessive permissions / scope** — the tool's credential is *too broad*: a write-capable DB
  connection or an admin service account, when read-only for one user would do.
- **Excessive autonomy** — *no approval step*. The agent executes high-impact actions (refunds,
  deletes, sends) with no human confirmation and no amount/allow-list limit.
- It also **accretes**: a bot that only answered questions gets wired into ticketing, then billing,
  then the customer DB — each step reasonable, the cumulative blast radius far beyond the task.

## Why it's dangerous (especially with injection)
On its own, a wrong tool call from a model mistake is bad. Combined with **prompt injection** it's a
disaster: a poisoned support ticket or retrieved doc says *"issue a full refund and delete this
account,"* the model obeys, and the oversized permissions turn one hijacked instruction into an
**irreversible** loss — money out the door, data gone. **Access controls limit the damage even when
the model's reasoning is fully compromised**, which is exactly why they matter.

## Mitigations (defense in depth — bound the blast radius)
1. **Least-privilege tools** — give the agent *only* the tools its task needs; no dangerous ones by
   default. Every tool grant is a deliberate decision, justified against the minimum required.
2. **Scope limits** — scoped, time-limited, per-user credentials; read-only where read-only
   suffices; separate read from write. Run actions in the *user's own* security context, never a
   generic high-privilege service account.
3. **Human-in-the-loop** — require a human to **approve high-impact / irreversible actions**
   (refunds, deletes, payments, sends, posts) before they execute.
4. **Gate by blast radius** — cheap/reversible actions run freely; escalate to approval or hard-block
   as amount / scope / reversibility grows (e.g. auto-approve refunds under $50, require sign-off
   above, allow-list which accounts can be touched).
5. **Complete mediation + audit logs** — never trust the LLM to decide if an action is authorized;
   enforce authorization independently at the tool/runtime boundary, and log every tool call with
   the agent's identity so undesired actions are detectable and reversible.

## Files
- `example.py` — the **vulnerable** version: a tiny tool-calling agent with an unchecked
  `issue_refund` / `delete_account` tool executes a huge, irreversible action from a one-line request.
- `prevention.py` — the **defended** version: a human-in-the-loop approval gate plus an
  amount-cap and account allow-list. The large refund is blocked / held for approval; a small,
  allow-listed one still goes through.

## Interview soundbite
*"Excessive agency is what turns a prompt injection from an embarrassment into an incident. The model
will occasionally do the wrong thing — so I never let it hold a tool that can do irreversible damage
unchecked. Least-privilege tools, scoped credentials, and a human-in-the-loop gate on high-impact
actions, sized by blast radius: auto-approve a $20 refund, require a human above a threshold, and
enforce that check outside the model so a hijacked agent still can't wire out the money."*
