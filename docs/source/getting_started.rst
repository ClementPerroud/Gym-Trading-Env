Gettings Started
==============

Installation
---------------

Crypto Trading Env supports Python 3.9+ on Windows, Mac, and Linux. You can install PyBroker using pip:

.. code-block:: console

   pip install gym-trading-env

Or using git :

.. code-block:: console
   
   git clone https://github.com/ClementPerroud/Gym-Trading-Env


You must know
----------------------

Positions
~~~~~~~~~~

I have seen many environments that consider actions such as BUY, SELL. In my experience, it is a mistake to consider a reinforcement learning agent in the same way as a trader. Because, behind a trade, what really matter is the : **position reached**. In the environment, we label each position by a number :
*example with pair BTC/USDT*

* ``1`` : All of our portfolio is converted into BTC. **(=BUY ALL)**
* ``0`` : All of our portfolio is converted into USDT. **(=SELL ALL)**
*Now, we can imagine half position and other variants :*

* ``0.5`` : 50% in BTC & 50% in USDT
* Even : ``0.1`` : 10% in BTC & 90% in USDT ....
In fact, it is way simpler for a RL-agent to work with positions. This way, it can easily make complex operation with a simple action space.

.. code-block::python
  
    positions = [0, 0.5, 1]
    #... environment has been initialized with your positions list on pair BTC/USDT
    _ = env.step(1)
    # You just told the environment the reached the position : positions[1] = 0.5 ! The environment manages the trades to reach this 50% BTC, 50% USDT
 

Complex positions
~~~~~~~~~~

This environment supports more complex positions such as:

* ``-1`` : Bet 100% of the portfolio value on the decline of BTC (=SHORT). To perform this action, the environment borrows 100% of the portfolio valuation as stock Y to an imaginary person, and immediately sells it. When the agent closes this position, the environment buys the owed amount of stock Y and repays the imaginary person with it. If the price has fallen during the operation, we buy cheaper than we sold what we need to repay : the difference is our gain. The imaginary person is paid a small rent (parameter : borrow_interest_rate).
* ``+2`` : Bet 100% of the portfolio value of the rise of asset Y. We use the same mechanism explained above, but we borrow currency and buy stock Y.
* ``-10`` ? : We can BUT ... We need to borrow 1000% of the portfolio valuation as asset Y. You need to understand that such a "leverage" is very risky. As if the stock price rise by 10%, you need to repay the original 1000% of your portfolio valuation at 1100% (1000%*1.10) of your current portfolio valuation. Well, 100% (1100% - 1000%) of your portfolio is used to repay your debt. GAME OVER, you have 0$ left. The leverage is very useful but also risky, as it increases your gains AND your losses. Always keep in mind that you can lose everything.
