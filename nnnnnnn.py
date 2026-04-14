from flask import Flask, request, render_template_string

# ---------------- Expert System Shell ----------------
class ExpertSystemShell:
    def __init__(self):
        self.facts = set()
        self.rules = []

    def add_fact(self, fact):
        fact = fact.strip().lower()
        if fact not in self.facts:
            self.facts.add(fact)

    def add_rule(self, conditions, conclusion):
        self.rules.append((set(c.lower() for c in conditions), conclusion.lower()))

    def infer(self):
        added_new_fact = True
        while added_new_fact:
            added_new_fact = False
            for conditions, conclusion in self.rules:
                if conditions.issubset(self.facts) and conclusion not in self.facts:
                    self.add_fact(conclusion)
                    added_new_fact = True

    def query(self, fact):
        return fact.lower() in self.facts

# ---------------- Flask App ----------------
app = Flask(__name__)
es = ExpertSystemShell()

# Preload some rules
es.add_rule(["it is raining", "i have an umbrella"], "i will go outside")
es.add_rule(["i will go outside"], "i will get fresh air")
es.add_rule(["it is raining"], "the ground will be wet")

# HTML template (inline for simplicity)
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Expert System Demo</title>
</head>
<body>
    <h1>Expert System Shell (Flask)</h1>
    <form method="POST">
        <label>Enter a fact:</label>
        <input type="text" name="fact" required>
        <button type="submit">Add Fact</button>
    </form>
    <h2>Known Facts:</h2>
    <ul>
        {% for fact in facts %}
            <li>{{ fact }}</li>
        {% endfor %}
    </ul>
    <h2>Query a Fact:</h2>
    <form method="GET">
        <input type="text" name="query" placeholder="Enter fact to check">
        <button type="submit">Check</button>
    </form>
    {% if query_result is not none %}
        <p><strong>Query Result:</strong> {{ query_result }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    query_result = None

    if request.method == "POST":
        fact = request.form.get("fact", "").strip()
        if fact:
            es.add_fact(fact)
            es.infer()

    if request.method == "GET" and "query" in request.args:
        fact_to_check = request.args.get("query", "").strip()
        if fact_to_check:
            query_result = es.query(fact_to_check)

    return render_template_string(TEMPLATE, facts=sorted(es.facts), query_result=query_result)

if __name__ == "__main__":
    app.run(debug=True)
