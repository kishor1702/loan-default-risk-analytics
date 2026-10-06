# Project Notes

## Why I chose this project

Credit-risk problems are a good way to combine the three tools I use most in analytics: SQL, Python and Power BI.

I wanted the project to go beyond a dashboard and show the full path from raw data to a business decision.

## The question

If a lender has a large portfolio of applications:

- Which segments are showing higher default rates?
- What characteristics are associated with higher risk?
- Can a model rank applications by probability of default?
- Can those predictions be turned into something a business team can act on?

## What I did

I first used PostgreSQL to organise the data and understand the portfolio.

Then I moved to Python for feature engineering and modelling. I kept Logistic Regression as a baseline and compared it with LightGBM.

After that, I used SHAP to understand the model rather than treating the prediction as a black box.

Finally, I created a business layer with risk bands and expected-loss estimates and prepared the Power BI layer for reporting.

## What I learned

The biggest lesson from the project was that a good model is only one part of an analytics solution.

The useful part is connecting:

`data → analysis → prediction → explanation → business action`

## Interview version

> "I worked on a loan default risk project where I used PostgreSQL for data preparation and portfolio analysis, Python for feature engineering and predictive modelling, and Power BI for reporting. I started with Logistic Regression as a baseline and compared it with LightGBM. I then used SHAP to understand the important drivers and converted the predicted probability of default into risk bands and an expected-loss view. The main goal was to make the analysis useful to a business user, not just build a model."

## What I would not claim

I would not describe this as a production credit-underwriting system.

The dataset is public, LGD is illustrative, and the current validation approach should be replaced with out-of-time validation when a reliable decision-date field is available.
