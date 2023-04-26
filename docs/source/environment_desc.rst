Environment summary
============

.. image:: images/render.gif
  :width: 600
  :align: center
  
This environment is a `Gymnasium <https://gymnasium.farama.org/content/basic_usage/>`_ environment made for trading.

.. list-table:: Title
   :widths: 25 70
   :header-rows: 0
   
   * - Action Space
     - ``Discrete(N_positions)``
   * - Observation Space
     - ``Box( -np.inf, +np.inf, shape = ...)``
   * - Import
     - ``gymnasium.make("TradingEnv", df = df)
