.. meta::
   :title: Crypto Trading Environment
   :description: A crypto Trading Environment for Reinforcement Learning

.. title:: Crypto Trading Environment for Reinforcement Learning



|Crypto Trading Environment|
================================

.. |Crypto Trading Environment| raw:: html

   <h1 align='center'>
      <img src = 'https://github.com/ClementPerroud/Gym-Trading-Env/raw/main/docs/source/images/logo_light-bg.png' width='500'>
   </h1>

 
.. raw:: html

   <section class="shields" align="center">
      <a href="https://www.python.org/">
         <img src="https://img.shields.io/badge/python-v3-brightgreen.svg"
            alt="python">
      </a>
      <a href="https://pypi.org/project/gym-trading-env/">
         <img src="https://img.shields.io/badge/pypi-v1.1.3-brightgreen.svg"
            alt="PyPI">
      </a>
      <a href="https://github.com/ClementPerroud/Gym-Trading-Env/blob/main/LICENSE.txt">
      <img src="https://img.shields.io/badge/license-MIT%202.0%20Clause-green"
            alt="Apache 2.0 with Commons Clause">
      </a>
      <a href='https://gym-trading-env.readthedocs.io/en/latest/?badge=latest'>
          <img src='https://readthedocs.org/projects/gym-trading-env/badge/?version=latest' alt='Documentation Status' />
      </a>
      
      <br>
      <a href="https://github.com/ClementPerroud/Gym-Trading-Env">
         <img src="https://img.shields.io/github/stars/ClementPerroud/gym-trading-env?style=social" alt="Github stars">
      </a>
   </section>
  
Crypto Trading Env is an OpenAI Gym environment for simulating stocks and training Reinforcement Learning (RL) trading agents.
It was designed to be fast and customizable for easy RL trading algorithms implementation.

+---------------------------------------------------------------------------------+
| `Github <https://github.com/ClementPerroud/Gym-Trading-Env>`_  |
+---------------------------------------------------------------------------------+

Key features
---------------

This package aims to greatly simplify the research phase by offering :

* Easy and quick download technical data on several exchanges
* A simple and fast environment for the user and the AI, but which allows complex operations (Short, Margin trading).
* A high performance rendering (can display several hundred thousand candles simultaneously), customizable to visualize the actions of its agent and its results.
* (Coming soon) An easy way to backtest any RL-Agents or any kind

.. image:: images/render.gif

Installation
---------------

Crypto Trading Env supports Python 3.9+ on Windows, Mac, and Linux. You can install it using pip:

.. code-block:: console

   pip install gym-trading-env

Or using git :

.. code-block:: console
   
   git clone https://github.com/ClementPerroud/Gym-Trading-Env

   
Contents
---------------

.. toctree::
   
   Introduction <self>
   getting_started

.. toctree::
   :caption: 🤖 Reinforcement Learning
   
   rl_tutorial
   customization
   multi_datasets
   vectorize_env

.. toctree:: 
   :caption: 🦾 Functionnalities
   
   render
   download

.. toctree::
   :caption: 📈 Backtest
   
   backtest
 
.. toctree::
   :caption: 📚 Reference
   
   history
   documentation
