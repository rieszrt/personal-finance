import dotmap
import logging

class Simulatable():
    def __init__(self, children=[]):
        self.children = children.copy()
        self.ticks = 0

    def add_child(self, simulatable):
        simulatable.ticks = self.ticks
        self.children.append(simulatable)
        return simulatable

    def tick(self):
        self._do_pre_tick()
        self.ticks += 1
        for simulatable in self.children:
            simulatable.tick()
        self._do_post_tick()

    def _do_pre_tick(self):
        pass

    def _do_post_tick(self):
        pass

    def dump(self):
        child_dumps = []
        for simulatable in self.children:
            child_dumps.append(simulatable.dump())
        return "({}, ({}))".format(self._do_dump(), ",".join(child_dumps)) if child_dumps != [] else "({})".format(self._do_dump())
    
    def _do_dump(self):
        return "{} ({})".format(str(self), vars(self))

class ExpGrowth(Simulatable):
    def __init__(self, initial_value, growth_rate):
        super().__init__()
        self.current_value = initial_value
        self.growth_rate = growth_rate
        self.initial_value = initial_value

    def _do_post_tick(self):
        self.current_value = self.current_value * (1.0 + self.growth_rate)
 
    def get_initial(self):
        return self.initial_value

    def get(self):
        return self.current_value

    def set(self, new_value):
        self.current_value = new_value

    def add(self, addition):
        self.current_value += addition

class Asset(Simulatable):
    def __init__(self):
        super().__init__()
        pass

    def get_income(self):
        return 0.0

    def get_value(self):
        return 0.0

    def get_cost(self):
        return 0.0

class Portfolio(Asset):
    def do_invest(self, cash):
        pass

    def get_value(self):
        return 0.0

    def get_income(self):
        return 0.0

    def get_cost(self):
        return 0.0

class ShareInvestmentPortfolio(Portfolio):
    def __init__(self, growth_rate, income_rate=0.0, value=0.0):
        super().__init__()
        self.value = self.add_child(ExpGrowth(value, growth_rate))
        self.income_rate = income_rate

    def do_invest(self, cash):
        return self.value.add(cash)

    def get_value(self):
        return self.value.get()

    def get_income(self):
        return self.value.get() * self.income_rate

class CashPortfolio(Portfolio):
    def __init__(self, interest_rate, value=0.0):
        super().__init__()
        self.value = value
        self.interest_rate = interest_rate

    def do_invest(self, cash):
        self.value += cash

    def get_value(self):
        return self.value

    def get_income(self):
        return self.value * self.interest_rate

class Employment(Asset):
    def get_income(self):
        return 0.0

class CareerEmployment(Employment):
    def __init__(self, initial_salary, cpi_growth_rate, maximum_salary=None, maturity_age=None):
        super().__init__()
        if maximum_salary is None or maturity_age is None:
            maximum_salary = initial_salary
            maturity_age = 1.0
        self.minimum_salary = self.add_child(ExpGrowth(initial_salary, cpi_growth_rate))
        self.maximum_salary = self.add_child(ExpGrowth(maximum_salary, cpi_growth_rate))
        self.maturity_age = maturity_age

    def get_income(self):
        salary_spread = self.maximum_salary.get() - self.minimum_salary.get()
        age_benefit = min(self.maturity_age, self.ticks) / float(self.maturity_age)
        current_salary = self.minimum_salary.get() + age_benefit * salary_spread
        return current_salary

class Environment(Asset):
    def get_cost(self):
        return 0.0

class LivingEnvironment(Asset):
    def __init__(self, initial_cost, cpi_growth_rate):
        super().__init__()
        self.initial_cost = initial_cost
        self.reference_cost = self.add_child(ExpGrowth(1.0, cpi_growth_rate))

    def get_cost(self):
        return self.reference_cost.get() * self.initial_cost

    def get_reference_cost(self):
        return self.reference_cost.get()

class World(Simulatable):
    def get_value(self):
        return 0.0

class Housing(Asset):
    def get_cost(self):
        return 0.0

    def get_value(self):
        return 0.0

    def get_taxed_value(self):
        return 0.0

class MortgageHousing(Asset):
    def __init__(self, initial_deposit, initial_value, value_growth_rate, duration, repayment, costs, costs_growth_rate):
        super().__init__()
        self.total_equity = self.add_child(ExpGrowth(initial_value, value_growth_rate))
        self.ownership = initial_deposit / initial_value if initial_value != 0.0 else 0.0
        self.duration = duration
        self.ownership_increase = (1.0 - self.ownership) / float(self.duration)
        self.repayment = repayment
        self.costs = self.add_child(ExpGrowth(costs, costs_growth_rate))

    def get_cost(self):
        return self.costs.get() + (self.repayment if self.ticks <= self.duration else 0.0)

    def get_value(self):
        return self.total_equity.get() * self.ownership

    def get_taxed_value(self):
        total_equity = self.total_equity.get()
        capital_gain = total_equity - self.total_equity.get_initial()
        taxed_total_equity = total_equity - capital_gain * (0.325/2.0)
        return taxed_total_equity * self.ownership

    def _do_post_tick(self):
        self.ownership = min(self.ownership + self.ownership_increase, 1.0)

class InvestmentProperty(MortgageHousing):
    def __init__(self, initial_deposit, initial_value, value_growth_rate, duration, repayment_total, repayment_interest_only, costs, costs_growth_rate, rent, rent_growth_rate):
        super().__init__(initial_deposit, initial_value, value_growth_rate, duration, repayment_total, costs, costs_growth_rate)
        self.rent = self.add_child(ExpGrowth(rent, rent_growth_rate))
        self.repayment_interest = repayment_interest_only

    def get_deductions(self):
        return self.costs.get() + (self.repayment_interest if self.ticks <= self.duration else 0.0)

    def get_income(self):
        return self.rent.get()

    def _do_post_tick(self):
        super()._do_post_tick()

        logging.info("InvestmentProperty: Year: {}, Income: {}, Cost: {}, Deductions: {}".format(self.ticks, self.get_income(), self.get_cost(), self.get_deductions()))

class TaxOffice(Asset):
    def __init__(self, args):
        super().__init__()
        self.hecs_debt = self.add_child(ExpGrowth(args.hecs_debt, args.hecs_growth_rate))

    def do_tax(self, taxable_income):
        tax = (taxable_income * 0.325 ) + 5092.0
        medicare_levy = taxable_income * 0.02

        total_tax = tax + medicare_levy
        return taxable_income - total_tax

    def get_value(self):
        return (-self.hecs_debt.get())
"""
class PropertyPortfolio(Asset):
    def __init__(self, args):
        super().__init__()
        self.bank_cash = 0.0 
        self.properties = []
        self.args = args
        self.property_price = self.add_child(ExpGrowth(args.value, args.value_growth_rate))

    def do_invest(self, cash):
        self.bank_cash += cash
        self._attempt_purchase()

    def _attempt_purchase(self):
        pass

    def _do_purchase(self):
        new_property = None #InvestmentProperty(self.purchase_property)
        self.add_properties(new_property)

    def add_property(self, new_property)
        self.properties.append(new_property) 
        self.add_child(new_property)

    def get_income(self):
        bank_interest = self.bank_cash * (self.args.bank_interest_rate)
        return bank_interest
"""
class SimpleWorld(World):
    def __init__(self, args):
        super().__init__()

        self.housing = MortgageHousing(
            args.mortgage.deposit,
            args.mortgage.value,
            args.mortgage.value_growth_rate,
            args.mortgage.duration,
            args.mortgage.repayment,
            args.mortgage.ongoing_costs,
            args.mortgage.ongoing_costs_growth_rate)
        self.employment = CareerEmployment(
            args.career.initial_salary,
            args.environment.inflation_rate,
            maximum_salary=args.career.maximum_salary,
            maturity_age=args.career.maturity_age)
        self.share_portfolio = ShareInvestmentPortfolio(
            args.shares.growth_rate,
            income_rate=args.shares.income_rate,
            value=args.assets.savings)
        self.property_portfolio = InvestmentProperty(
            args.investment_property.deposit,
            args.investment_property.value,
            args.investment_property.value_growth_rate,
            args.investment_property.duration,
            args.investment_property.repayment,
            args.investment_property.repayment_interest,
            args.investment_property.ongoing_costs,
            args.investment_property.ongoing_costs_growth_rate,
            args.investment_property.rent,
            args.investment_property.rent_growth_rate)
        self.tax_office = TaxOffice(args.tax)
        self.environment = LivingEnvironment(
            args.lifestyle.living_cost,
            args.environment.inflation_rate)

        self.add_child(self.housing)
        self.add_child(self.employment)
        self.add_child(self.share_portfolio)
        self.add_child(self.property_portfolio)
        self.add_child(self.tax_office)
        self.add_child(self.environment)

    def _do_post_tick(self):
        employment_income = self.employment.get_income()
        passive_income = sum([
            self.share_portfolio.get_income(),
            self.property_portfolio.get_income(),
            self.environment.get_income()])
        
        gross_income = employment_income + passive_income

        property_portfolio_deductions = self.property_portfolio.get_deductions()

        deductions = property_portfolio_deductions
        
        taxable_income = max(0, gross_income - deductions)
        
        post_tax_income = self.tax_office.do_tax(taxable_income)

        property_portfolio_non_deductions = self.property_portfolio.get_cost() - property_portfolio_deductions

        living_cost = sum([
            self.environment.get_cost(),
            self.housing.get_cost(),
            property_portfolio_non_deductions])

        spare_cash = post_tax_income - living_cost

        self.share_portfolio.do_invest(spare_cash)

        logging.info("Year: {}, Income: {}, Passive-Income: {}, Cost: {}, Post-Tax: {}, Spare: {}, Total-Adjusted: {}".format(self.ticks, taxable_income, passive_income, living_cost, post_tax_income, spare_cash, self.get_cost_adjusted_value()))
        logging.debug("Year: {}, Dump: {}".format(self.ticks, self.dump()))

    def get_value(self):
        return (self.share_portfolio.get_value() + self.property_portfolio.get_taxed_value()) + self.housing.get_value() + self.tax_office.get_value()

    def get_cost_adjusted_value(self):
        return self.get_value() / self.environment.get_reference_cost()
