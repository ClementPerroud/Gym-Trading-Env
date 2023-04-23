Advanced
==========

History object
--------------


Custom logs
-------------

If `verbose` parameters of your trading environment is set to `1` or `2`, the environment display a quick summary of your episode. By default `Market Return` and `Portfolio Return` are the displayed metrics.

.. code-block:: bash

  Market Return :  25.30%   |   Portfolio Return : 45.24%

You can add custom metrics using the method `.add_metric(name, function)` after initializing your environment :

.. code-block:: python
  
  #After env.make(...)
  env.add_metric('Position Changes', lambda history : np.sum(np.diff(history['position']) != 0) )
  env.add_metric('Episode Lenght', lambda history : len(history['position']) )
  # Then, run your episode(s)

.. code-block:: bash

  Market Return :  25.30%   |   Portfolio Return : 45.24%   |   Position Changes : 28417   |   Episode Lenght : 33087

The `.add_metric` method takes 2 parameters :

* `name` : The displayed name of the metrics

* `function` : The function that takes the history object as parameters and returns a value (we obviously prefer string over other types here). More information about the history object here.

