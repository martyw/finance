Finance
=======

A collection of building blocks to study some finance concepts, such as option pricing with Black & Scholes, a limit order book to simulate a stock exchange, algo trading and much more. 
I took a lot of inspiration from snippets found across the internet.
Important note: this code is for educational purposes only! See also the license.....

Features
=========

- Central Limit Order book
- Options pricing
- Bond pricing
- Algo trading
- Curves for modelling interest rates and bootstrapping zero rate curves
- Surfaces for volatility smile
- Calculate time to expiry from python date objects Excel style

Requirements
============

Code is tested with Python 3.7. Needed modules not part of the sytandard release are
- sortedcontainers
- numpy
- scipy
- pandas
- matplotlib
- requests_cache

All software is tested on Ubuntu Linux, no OS specific features are used in the code.

Usage
=====

The main modules mentioned here have either unit tests where many examples are covered, or example code on how to use the code 

Limit order book
----------------
Main module for the limit order book is `orderbook/matching_engine.py`.

Options pricing
---------------

Main module for the Black and Scholes option pricing is `options/black_scholes.py`.
Curves and surfaces are also applied in the Black and Scholes pricer `options/black_scholes.py`.
Date calculations needed by the pricer are in `utils/date/yearfrac.py`, this module demonstrates various day count conventions as used in finance.

Bond pricing
------------

Main module for bond pricing is `securities/bond.py`.

Algo Trading
------------

Main module is `back_test_strategy.py`, this module illustrates how a mean reverting algo works based on a year of historical closings for an example stock.

Term structures
---------------

Bootstrapping the yield curve from bonds is in `term_structures/bootstrap.py`. 
The volatility surface is in `term_structures/surface.py`. 
