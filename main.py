####################################################################
# Azure reader for Python
# Performance Metrics being read: Available Memory Bytes, Percentage CPU
####################################################################

from azure.identity import AzureCliCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
import json
import datetime
import lzma
import uuid

FILENAME = "saveddata.bin.lzma"
VERSION = 2
METRICS_TO_READ = ["Percentage CPU", "Available Memory Bytes"]


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()
sub_client = SubscriptionClient(credential)

saveddata = {}
try:
    subs = [sub.as_dict() for sub in sub_client.subscriptions.list()]
except Exception as e:
    print(f"Error: {e}")
    exit()

if len(subs) == 0:
    print("No subscriptions available for your user.")
    exit()

print("Please inform your company name: ", end="")
company_name = input()
saveddata["subscriptions"] = subs
vm_list = []
vm_metrics = []
today = datetime.datetime.utcnow()
last_month = today - datetime.timedelta(days=30)

for sub in subs:
    temp_vm_list = []
    temp_vm_metrics = []
    subscription_id = sub["subscription_id"]

    print(f"Reading the VM List for subscription {subscription_id}")
    compute_client = ComputeManagementClient(credential, subscription_id)
    try:
        for vm in compute_client.virtual_machines.list_all():
            vmdict = vm.as_dict()
            vmdict["subscription"] = subscription_id
            temp_vm_list.append(vmdict)
    except:
        print(
            f"Error getting the VM List. Please check your Azure's Subscription ID. The one tried was {subscription_id}"
        )
        exit()
    print(f"Total VM Count = {len(temp_vm_list)}")

    vm_list.extend(temp_vm_list)

    ####################################################################
    # Get the performance metrics
    ####################################################################

    print("\nGetting VMs' Performance Metrics")
    monitor_client = MonitorManagementClient(credential, subscription_id)

    for vm in temp_vm_list:
        resource_id = vm["id"]
        metrics = []
        for metric_type in METRICS_TO_READ:

            metrics_data = monitor_client.metrics.list(
                resource_id,
                timespan="{}/{}".format(last_month, today),
                interval="PT15M",
                metricnames=metric_type,
                aggregation="Average",
            )

            for item in metrics_data.value:
                # azure.mgmt.monitor.models.Metric
                for timeserie in item.timeseries:
                    times = []
                    for data in timeserie.data:
                        # azure.mgmt.monitor.models.MetricData
                        if data.average == None:
                            continue
                        times.append(
                            {"time_stamp": data.time_stamp, "average": data.average}
                        )

                    metrics.append(
                        {
                            "localized_value": item.name.localized_value,
                            "unit": item.unit,
                            "times": times,
                        }
                    )
        temp_vm_metrics.append({"vm": vm, "metrics": metrics})
    vm_metrics.extend(temp_vm_metrics)

saveddata["metrics"] = vm_metrics
saveddata["vm_list"] = vm_list
saveddata["version"] = VERSION  # With the new format
saveddata["processed_date"] = today
saveddata["id"] = str(uuid.uuid4())
saveddata["customer_name"] = company_name
saveddata["csp"] = "Azure"

print("\nPerformance Metrics finished. Saving the data")

# Save to the directory
try:
    with lzma.open(FILENAME, "wt", encoding="ascii") as f:
        json.dump(saveddata, f, default=str)

except Exception as E:
    print(f'Error saving file "{FILENAME}". Error = {E}')
    exit()
print(f'Report saved successfully to "{FILENAME}"')
