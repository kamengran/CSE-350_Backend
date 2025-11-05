from flask import Flask, request, jsonify
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---------- ROUTES START ----------

    # 1️⃣ FINANCIAL AID
    @app.route("/calc/financial_aid", methods=["POST"])
    def calc_financial_aid():
        data = request.get_json(force=True) or {}
        coa = float(data.get("costOfAttendance", 0))
        grants = float(data.get("grants", 0))
        scholarships = float(data.get("scholarships", 0))
        work_study = float(data.get("workStudy", 0))
        efc = float(data.get("efc", 0))

        gift_aid = grants + scholarships
        remaining_need = max(coa - gift_aid - work_study - efc, 0)
        sub_cap = 3500
        subsidized = min(remaining_need, sub_cap)
        unsubsidized = max(remaining_need - subsidized, 0)

        return jsonify({
            "costOfAttendance": coa,
            "efc": efc,
            "giftAid": gift_aid,
            "remainingNeed": remaining_need,
            "suggestedLoans": {"subsidized": subsidized, "unsubsidized": unsubsidized},
            "workStudy": work_study
        })


    # 2️⃣ BUDGET BUCKETS
    @app.route("/calc/buckets", methods=["POST"])
    def calc_buckets():
        data = request.get_json(force=True) or {}
        income = float(data.get("monthlyIncome", 0))

        needs = income * 0.50
        wants = income * 0.30
        savings = income * 0.20

        rent = needs * 0.60
        food = needs * 0.20
        transport = needs * 0.10
        utilities = needs * 0.10

        entertainment = wants * 0.60
        other = wants * 0.40

        return jsonify({
            "income": income,
            "needs": round(needs, 2),
            "wants": round(wants, 2),
            "savings": round(savings, 2),
            "buckets": {
                "rent": round(rent, 2),
                "food": round(food, 2),
                "transport": round(transport, 2),
                "utilities": round(utilities, 2),
                "entertainment": round(entertainment, 2),
                "other": round(other, 2),
                "savings": round(savings, 2)
            }
        })


    # 3️⃣ SAVINGS CALCULATOR
    @app.route("/calc/savings", methods=["POST"])
    def calc_savings():
        data = request.get_json(force=True) or {}
        goal = float(data.get("goal", 0))
        months = max(int(data.get("months", 1)), 1)
        apy = float(data.get("apy", 0))

        monthly_deposit = goal / months
        monthly_rate = (apy / 100.0) / 12.0
        balance = 0.0
        for _ in range(months):
            balance += monthly_deposit
            balance *= (1 + monthly_rate)

        return jsonify({
            "goal": round(goal, 2),
            "months": months,
            "apy": apy,
            "monthlyDeposit": round(monthly_deposit, 2),
            "projectedTotal": round(balance, 2)
        })

    @app.route("/calc/compare", methods=["POST"])
    def calc_compare():
        """
        Compare user's spending in a specific category against the recommended goal.

        Example request:
        {
            "monthlyIncome": 2000,
            "category": "Food",
            "items": [
                {"name": "groceries", "cost": 50},
                {"name": "snacks", "cost": 10}
            ]
        }
        """
        data = request.get_json(force=True) or {}
        income = float(data.get("monthlyIncome", 0))
        category = data.get("category", "Food")
        items = data.get("items", [])

        # Calculate goal using your /calc/buckets logic
        # (just reuse the ratio percentages)
        ratios = {
            "Rent": 0.35, "Food": 0.10, "Transport": 0.08, "Utilities": 0.07,
            "Health": 0.05, "Savings": 0.15, "Entertainment": 0.08, "Other": 0.012
        }
        goal = income * ratios.get(category, 0.05)

        # Calculate actual spending
        spent = sum(float(x.get("cost", 0)) for x in items)
        remaining = goal - spent

        return jsonify({
            "category": category,
            "goal": goal,
            "spent": spent,
            "remaining": remaining,
            "status": "ok" if remaining >= 0 else "over budget"
        })

    # ---------- ROUTES END ----------
    return app
