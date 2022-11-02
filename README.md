# dbt-metadata-client

The `dbt-metadata-client` is a utility package to make it easier to build queries to run against dbt's metadata API. Additonally it allows for, if you desire, parsing the response JSON into python class objects.

# Examples
```python
import os
from dbt_metadata_client.client import Client

# Buidling a Client is incredibly easy. All you need is a API key / service
# token to get started
dbt_api_key = os.getenv("DBT_API_KEY")
dbt_job_id = 1337
client = Client(api_token=dbt_api_key)

# Now with a Client you can begin runnin queries!
# The Client provides some base query helpers which return the fully defined
# object and one level of graph traversal. For example if you use the provided
# querier for metrics you get all the key/values for a metric and the first
# level objects linked to a metric, which for a metric is a model, but the
# objects linked to a model (parents_models, parents_sources, tests) won't get
# populated.
metrics = client.get_metrics(job_id=dbt_job_id)
print(metrics)

# [
#     MetricNode(
#         run_id=44444,
#         account_id=11111,
#         project_id=22222,
#         environment_id=33333,
#         job_id=1337,
#         resource_type='metric',
#         unique_id='metric.transform_dbt.amount',
#         name='amount',
#         description='Sum of amount',
#         meta={'team': 'Finance'},
#         dbt_version='1.3.0',
#         tags=[],
#         package_name='transform_dbt',
#         label='Amount',
#         type='sum',
#         calculation_method='sum',
#         sql='amount_usd',
#         expression='amount_usd',
#         environment_name='Production',
#         timestamp='created_date',
#         filters=[],
#         time_grains=['day', 'week', 'month'],
#         dimensions=['stage_name'],
#         depends_on=['model.transform_dbt.opportunity_base'],
#         model=ModelNode(
#             run_id=44444,
#             account_id=11111,
#             project_id=22222,
#             environment_id=33333,
#             job_id=1337,
#             ...
#         )
#     ),
#     ...
# ]

# If instead of getting everything + one level of objects, you want to get specific
# keys and multiple levels, you can build a custom operation. 
from dbt_metadata_client.dbt_metadata_api_schema import Query
from sgqlc.operation import Operation

# First we create an operation
op = Operation(Query)

# Then we can add base objects to the operation
# calling `.<thing>()` modifies the `op` in place
metrics = op.metrics(job_id=dbt_job_id)

# This thus far is the same as the query we did above. That is when
# you add a `.<thing>()` where the thing is another object, it by default
# adds all the keys + one level of object linking. Also we can see this by
# printing the op
print(op)

# query {
#   metrics(jobId: 1337) {
#     runId
#     accountId
#     projectId
#     environmentId
#     jobId
#     resourceType
#     uniqueId
#     name
#     description
#     meta
#     dbtVersion
#     tags
#     packageName
#     label
#     type
#     calculation_method
#     sql
#     expression
#     environmentName
#     timestamp
#     filters {
#       field
#       operator
#       value
#     }
#     timeGrains
#     dimensions
#     dependsOn
#     model {
#       runId
#       accountId
#       projectId
#       environmentId
#       jobId
#       resourceType
#       uniqueId
#       name
#       description
#       meta
#       dbtVersion
#       tags
#       database
#       schema
#       alias
#       invocationId
#       args
#       error
#       status
#       skip
#       compileStartedAt
#       compileCompletedAt
#       executeStartedAt
#       executeCompletedAt
#       executionTime
#       threadId
#       runGeneratedAt
#       runElapsedTime
#       dependsOn
#       packageName
#       type
#       owner
#       comment
#       childrenL1
#       rawSql
#       rawCode
#       compiledSql
#       compiledCode
#       materializedType
#     }
#   }
# }

# If we want to query this as is, we just pass it to the client
data = client.query_operation(op)
# And then following sgqlc's interesting format, we can parse it to class objects
from dbt_metadata_client.dbt_metadata_api_schema import MetricNode
metric_nodes: list[MetricNode] = (op + data).metrics

# However, if we want, we can instead scope the op down by calling `metrics.<specific_key>()`
metrics.name()
metrics.run_id()
metrics.account_id()
metrics.project_id()

# adding the four above keys specifically narrowed down our operation
print(op)

# query {
#   metrics(jobId: 1337) {
#     name
#     runId
#     accountId
#     projectId
#   }
# }

# we can also add sub objects
metrics_model = metrics.model()
metrics_model.name()
metrics_model_test = metrics_model.tests()
metrics_model_test.name()
metrics_model_test.status()

# and thus our query now looks like the following
print(op)

# query {
#   metrics(jobId: 1337) {
#     name
#     runId
#     accountId
#     projectId
#     model {
#       name
#       tests {
#         name
#         status
#       }
#     }
#   }
# }
```