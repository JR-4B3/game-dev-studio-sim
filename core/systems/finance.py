"""Money over time: the monthly books, living costs, loans, taxes and
bankruptcy. Every cash movement in the game goes through Game.earn, Game.spend
or Game.finance, so the books always add up."""
from ..content import FORMAT, LOAN, LOANS, RESEARCH_NODE, SUPPORT
from ..game import str_arg
from ..state import Ledger, Loan


def on_month(game):
    s = game.s.studio
    game.s.ledgers.append(Ledger(month=game.month_key()))
    del game.s.ledgers[:-24]
    game.spend("Living costs", game.b.start.living_costs)
    if game.date.month in (1, 4, 7, 10):
        if s.tax_base > 0:
            tax = s.tax_base * game.b.finance.tax_rate
            game.spend("Taxes", tax)
            s.tax_base = 0.0  # the tax itself was booked as an expense this quarter
            game.log(f"Paid ${tax:,.0f} in taxes on last quarter's profit.")
        # Losses carry forward until profits use them up.


def on_week(game):
    s, f = game.s.studio, game.b.finance
    for loan in list(s.loans):
        interest = loan.balance * loan.rate / 52
        principal = min(loan.balance, loan.weekly_payment - interest)
        game.spend("Interest", interest)
        game.finance("Loan repayment", -principal)
        loan.balance -= principal
        loan.weeks_left -= 1
        if loan.weeks_left <= 0 or loan.balance < 1:
            s.loans.remove(loan)
            game.log(f"Paid off the {loan.name.lower()}.")
    if s.cash < 0:
        s.insolvent_days += 7
        fee = -s.cash * f.overdraft_fee
        game.spend("Interest", fee)
        weeks = s.insolvent_days // 7
        left = f.bankruptcy_weeks - weeks
        if left <= 0:
            s.closed = "Bankrupt"
            game.log("The studio is bankrupt. The Campaign is over.")
        else:
            game.log(f"Cash is negative. {left} week{'s' if left != 1 else ''} until bankruptcy. Raise money or cut costs.")
    else:
        s.insolvent_days = 0


def credit_limit(game):
    s, f = game.s.studio, game.b.finance
    owed = sum(loan.balance for loan in s.loans)
    return max(0.0, f.credit_base + s.lifetime_revenue * f.credit_per_revenue + s.reputation * f.credit_per_reputation - owed)


def take_loan(game, data):
    s = game.s.studio
    rule = LOAN[str_arg(data, "name", LOAN)]
    if any(loan.name == rule["name"] for loan in s.loans):
        raise ValueError(f"You already have a {rule['name'].lower()}.")
    if rule["principal"] > credit_limit(game):
        raise ValueError(f"The bank declines. Your track record supports about ${credit_limit(game):,.0f} of credit.")
    rate = rule["rate"] + (0.04 if s.cash < 0 else 0)
    weekly = rate / 52
    payment = rule["principal"] * weekly / (1 - (1 + weekly) ** -rule["weeks"])
    s.loans.append(Loan(name=rule["name"], principal=rule["principal"], balance=rule["principal"], rate=rate,
                        weekly_payment=payment, weeks_left=rule["weeks"]))
    game.finance("Loans", rule["principal"])
    game.log(f"Took a {rule['name'].lower()}: ${rule['principal']:,.0f} at {rate:.1%}, ${payment * 4.33:,.0f} a month.")


def repay(game, data):
    s = game.s.studio
    name = str_arg(data, "name", LOAN)
    loan = next((l for l in s.loans if l.name == name), None)
    if not loan:
        raise ValueError("No such loan.")
    if s.cash < loan.balance:
        raise ValueError(f"Repaying needs ${loan.balance:,.0f}.")
    game.finance("Loan repayment", -loan.balance)
    s.loans.remove(loan)
    game.log(f"Repaid the {name.lower()} early.")


def rename(game, data):
    name = str_arg(data, "name").strip()
    if not 1 <= len(name) <= 40:
        raise ValueError("Studio names need 1 to 40 characters.")
    old = game.s.studio.name
    game.s.studio.name = name
    for p in game.s.products:
        if p.studio_id == 0:
            p.studio_name = name
    game.log(f"{old} is now called {name}.")


COMMANDS = {"loan": take_loan, "repay": repay, "rename": rename}


def monthly_costs(game):
    """What the studio will spend next month if nothing changes."""
    s, p = game.s.studio, game.b.people
    staff = [x for x in s.team if not x.founder]
    costs = {
        "Living costs": game.b.start.living_costs,
        "Salaries": sum(x.salary for x in staff) / 12 * (1 + p.employer_burden),
        "Workspace & tools": p.founder_tools + p.workspace_per_person * len(staff),
        "Research running costs": sum(RESEARCH_NODE[k].get("monthly", 0) for k in s.research_done),
        "Loans": sum(l.weekly_payment for l in s.loans) * 4.33,
        "Servers": sum((FORMAT[x.format]["server_rent"] * (1 + min(4, x.players / 50_000)) + x.players * FORMAT[x.format]["hosting"])
                       * SUPPORT[x.support]["hosting"] * 4.33 for x in game.s.products if x.studio_id == 0 and not x.retired),
    }
    return {k: round(v) for k, v in costs.items() if v}


def view(game):
    s = game.s.studio
    costs = monthly_costs(game)
    burn = sum(costs.values())
    recent = game.s.ledgers[-4:-1] or game.s.ledgers[-1:]
    income = sum(sum(l.income.values()) for l in recent) / len(recent)
    return {
        "studio": {"name": s.name, "cash": round(s.cash), "reputation": round(s.reputation, 1),
                   "insolvent_weeks": s.insolvent_days // 7, "lifetime_revenue": round(s.lifetime_revenue)},
        "monthly_costs": costs, "burn": burn, "average_income": round(income),
        "runway": round(s.cash / burn, 1) if burn and s.cash > 0 else 0,
        "ledgers": [{"month": l.month, "income": {k: round(v) for k, v in l.income.items()},
                     "expenses": {k: round(v) for k, v in l.expenses.items()},
                     "financing": {k: round(v) for k, v in l.financing.items()},
                     "net": round(sum(l.income.values()) - sum(l.expenses.values()))} for l in game.s.ledgers],
        "loans": [{"name": l.name, "balance": round(l.balance), "monthly": round(l.weekly_payment * 4.33),
                   "weeks_left": l.weeks_left, "rate": l.rate} for l in s.loans],
        "loan_offers": [{**rule, "taken": any(l.name == rule["name"] for l in s.loans)} for rule in LOANS],
        "credit_limit": round(credit_limit(game)), "bankruptcy_weeks": game.b.finance.bankruptcy_weeks,
    }
