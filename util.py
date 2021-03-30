def apply_marginal(base, table, value):
    acc = base
    brackets = sorted(table.keys())

    i = 0
    while i < len(brackets):
        if i == len(brackets) - 1:
            if value >= brackets[i]:
                acc += (value - brackets[i]) * table[brackets[i]]
        else:
            if value >= brackets[i] and value < brackets[i+1]:
                acc += (value - brackets[i]) * table[brackets[i]]
            elif brackets[i+1] < value:
                acc += (brackets[i+1] - brackets[i]) * table[brackets[i]]
        i += 1

    return acc

def calculate_loan_repayment(p, r, n):
    g = 1.0 + r
    total_owed = p * (g ** n)
    repayment = total_owed * ((1 - g) / (1 - g ** n))
    interest = (total_owed - p) / total_owed
    return (repayment, interest)

def calculate_loan_repayment_yearly(amount, yearly_rate, years):
    return calculate_loan_repayment(amount, yearly_rate, years)

#print(apply_marginal(10, {0.0: 0.0, 20000.0: 0.2, 50000.0: 0.35}, 0))
#print(calculate_loan_repayment(800000.0, 0.02, 30.0))
