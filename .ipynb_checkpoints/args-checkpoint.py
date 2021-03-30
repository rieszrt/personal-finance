import dotmap
import logging
from enum import Enum
import random

def use_base(base, updates):
    new_value = base.copy()
    new_value.update(updates)
    return new_value

class ParameterResolution(Enum):
    PESSIMISTIC = 0
    OPTIMISTIC = 1
    MIDDLE = 2
    RANDOM = 3

class Parameter():
    def get(self, resolution):
        return None

class RangeParameter(Parameter):
    def __init__(self, first, second):
        self.first = first
        self.second = second
        self.random = random.random()

    def get(self, resolution):
        if resolution == ParameterResolution.PESSIMISTIC or resolution == ParameterResolution.OPTIMISTIC or resolution == ParameterResolution.MIDDLE:
            return (self.second + self.first)/2.0
        if resolution == ParameterResolution.RANDOM:
            return self.first + (self.second - self.first) * self.random
        return None

class OrderedParameter(RangeParameter):
    def __init__(self, first, second):
        super().__init__(first, second)

    def get(self, resolution):
        if resolution == ParameterResolution.PESSIMISTIC:
            return self.first
        if resolution == ParameterResolution.OPTIMISTIC:
            return self.second
        if resolution == ParameterResolution.MIDDLE:
            return (self.second + self.first)/2.0
        if resolution == ParameterResolution.RANDOM:
            return self.first + (self.second - self.first) * self.random
        return None

def resolve_parameters(args, resolution):
    if type(args) == type({}):
        new_args = {}
        for arg_name in args:
            new_args[arg_name] = resolve_parameters(args[arg_name], resolution)
        return new_args

    if type(args) == type([]):
        new_args = []
        for arg in args:
            new_args.append(resolve_parameters(arg, resolution))
        return new_args
 
    if issubclass(type(args), Parameter):
        return args.get(resolution)

    return args

inflation_rate = 0.025
rent_growth_rate = inflation_rate
apartment_growth_rate = OrderedParameter(-0.01, inflation_rate)
house_growth_rate = OrderedParameter(0.05, 0.07)
property_ongoing_costs_growth_rate = OrderedParameter(0.035, inflation_rate)

living_cost_basic = 15000
living_cost_rent = OrderedParameter(15000 + 250*52, 15000 + 200*52)


career = ({
    "initial_salary": OrderedParameter(70000.0, 90000.0),
    "maximum_salary": OrderedParameter(120000.0, 140000.0),
    "maturity_age": 20.0})


mortgage_base = ({
    "deposit": 0,
    "value": 0,
    "value_growth_rate": 0.0,
    "duration": 30,
    "repayment": 0,
    "ongoing_costs": 0,
    "ongoing_costs_growth_rate": property_ongoing_costs_growth_rate})

mortgage_none = use_base(mortgage_base, {})

def make_mortgage_apartment(total_value):
    def calculate_unit_rates(total_value):
        return 808.0 + 0.005202 * total_value

    value = total_value / 2.0
    deposit = value * 0.2
    repayment = value * 0.04

    rates = calculate_unit_rates(total_value)
    maintainence_min = 0.008333 * total_value
    maintainence_max = 0.013333 * total_value
    utilities = 50.0*52.0

    ongoing_costs_base = (rates + maintainence_min + utilities) / 2.0
    ongoing_costs_maximum = (rates + maintainence_max + utilities) / 2.0

    mortgage = use_base(mortgage_base, {
        "deposit": deposit,
        "value": value,
        "value_growth_rate": apartment_growth_rate,
        "duration": 30.0,
        "repayment": repayment,
        "ongoing_costs": OrderedParameter(ongoing_costs_maximum, ongoing_costs_base)})
    return mortgage

mortgage_apartment = make_mortgage_apartment(300000.0)

mortgage_apartment_expensive = use_base(mortgage_base, {
    "deposit": 60000.0,
    "value": 300000.0,
    "value_growth_rate": apartment_growth_rate,
    "duration": 30.0,
    "repayment": 12000.0,
    "ongoing_costs": OrderedParameter(3000.0, 2000.0)})

mortgage_house = use_base(mortgage_base, {
    "deposit": 120000.0,
    "value": 600000.0,
    "value_growth_rate": house_growth_rate,
    "duration": 30,
    "repayment": 24000.0,
    "ongoing_costs": OrderedParameter(9800.0, 9000.0)})


investment_property_base = use_base(mortgage_base, {
    "repayment_interest": 0,
    "rent": 0,
    "rent_growth_rate": rent_growth_rate})

investment_property_none = use_base(investment_property_base, {})

investment_property_apartment = use_base(investment_property_base, {
    "deposit": 30000.0,
    "value": 150000.0,
    "value_growth_rate": apartment_growth_rate,
    "duration": 30.0,
    "repayment": 6000.0,
    "repayment_interest": 1800.0,
    "ongoing_costs": OrderedParameter(5700.0, 4700.0),
    "rent": OrderedParameter(8000.0, 9100.0)})
 
investment_property_house = use_base(investment_property_base, {
    "deposit": 120000.0,
    "value": 600000.0,
    "value_growth_rate": house_growth_rate,
    "duration": 30.0,
    "repayment": 24000.0,
    "repayment_interest": 7200.0,
    "ongoing_costs": OrderedParameter(18900.0, 17600.0),
    "rent": OrderedParameter(16120.0, 26000.0)})


lifestyle_none = ({
    "living_cost": 0})

lifestyle_minimal = ({
    "living_cost": 6000})

lifestyle_no_rent = ({
    "living_cost": living_cost_basic})

lifestyle_rent = ({
    "living_cost": living_cost_rent})


shares_aus = ({
    "growth_rate": OrderedParameter(0.043, 0.054),
    "income_rate": OrderedParameter(0.02, 0.025)})

shares_us = ({
    "growth_rate": OrderedParameter(0.05, 0.057),
    "income_rate": OrderedParameter(0.015,0.02)})

shares_cash_etf = ({
    "growth_rate": 0.0,
    "income_rate": inflation_rate})

shares = shares_aus


assets_all = ({
    "savings": 120000.0})

assets_minus_apartment = ({
    "savings": 90000.0})

assets_minus_apartment_expensive = ({
    "savings": 60000.0})

assets_none = ({
    "savings": 0.0})

tax = {
    "hecs_debt": 30000.0,
    "hecs_growth_rate": inflation_rate}

environment = ({
    "inflation_rate": inflation_rate})


args_base = ({
    "career": career,
    "shares": shares,
    "mortgage": mortgage_none,
    "investment_property": investment_property_none,
    "lifestyle": lifestyle_rent,
    "assets": assets_all,
    "tax": tax,
    "environment": environment})

args_no_costs = use_base(args_base, {"lifestyle": lifestyle_none})

args_minimal = use_base(args_base, {"lifestyle": lifestyle_minimal})

args_rent = use_base(args_base, {})

args_apartment = use_base(args_base, {
    "mortgage": mortgage_apartment,
    "lifestyle": lifestyle_no_rent,
    "assets": assets_minus_apartment})

args_apartment_expensive = use_base(args_base, {
    "mortgage": mortgage_apartment_expensive,
    "lifestyle": lifestyle_no_rent,
    "assets": assets_minus_apartment_expensive})

args_house = use_base(args_base, {
    "mortgage": mortgage_house,
    "lifestyle": lifestyle_no_rent,
    "assets": assets_none})

args_rentvest_apartment = use_base(args_base, {
    "investment_property": investment_property_apartment,
    "assets": assets_minus_apartment})

args_rentvest_house = use_base(args_base, {
    "investment_property": investment_property_house,
    "assets": assets_none})

args_rent_cash = use_base(args_base, {"shares": shares_cash_etf})
