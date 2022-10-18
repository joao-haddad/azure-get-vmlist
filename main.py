####################################################################
# Azure reader for Python
####################################################################

from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.monitor import MonitorManagementClient
import os
import pickle
from datetime import date
import datetime
from dataclasses import dataclass
from typing import List

# PLEASE UPDATE THE SUBSCRIPTION_ID BELOW:
SUBSCRIPTION_ID = "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
FILENAME_METRICS = "savedmetricsdata.bin"
FILENAME_VMLIST = "savedvmlistdata.bin"

# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()

# Retrieve subscription ID from environment variable.
from azure.mgmt.compute import ComputeManagementClient

vm_list = []

@dataclass
class Virtual_Machine_Type:
    name: str
    location: str
    id: str
    plan: str
    vm_size: str
    os_type: str
    create_date: date

####################################################################
#Get the VM List, only keeping the attributes above
####################################################################

print ("Reading the VM List")

compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)
try:
    for vm in compute_client.virtual_machines.list_all():
        temp = vm.as_dict()
        os_type = "Other"
        if (vm.os_profile.linux_configuration != None):
            os_type = "Linux"
        if (vm.os_profile.windows_configuration != None):
            os_type = "Windows"
        vm_list.append(Virtual_Machine_Type(vm.name, vm.location, vm.id, vm.plan, vm.hardware_profile.vm_size, os_type, vm.time_created))
except:
    print (f"Error getting the VM List. Please check your Azure's Subscription ID. The one tried was {SUBSCRIPTION_ID}")
    exit()
print (f"Total VM Count = {len(vm_list)}")

print (vm_list)

####################################################################
#Get the performance metrics
####################################################################

@dataclass
class Time_Stamp:
    pooling_time: date
    result: float

@dataclass
class Metric_Type:
    metric_name: str
    metric_unit: str
    results: List[Time_Stamp]


@dataclass
class VM_Metrics:
    vm_info: Virtual_Machine_Type
    results: List[Metric_Type]

print ("\nGetting the Performance Metrics for the VMs")

monitor_client = MonitorManagementClient(credential, SUBSCRIPTION_ID)

today = datetime.datetime.utcnow()
last_month = today - datetime.timedelta(days=30)
vm_metrics = []

for vm in vm_list:
    resource_id = vm.id
    metrics_data = monitor_client.metrics.list(
        resource_id,
        timespan="{}/{}".format(last_month, today),
        interval='PT5M',
        metricnames='Percentage CPU',
        aggregation='Average'
    )
    metrics = []

    for item in metrics_data.value:
        # azure.mgmt.monitor.models.Metric
        for timeserie in item.timeseries:
            times = []
            for data in timeserie.data:
                # azure.mgmt.monitor.models.MetricData
                if (data.average == None):
                    continue
                times.append (Time_Stamp(data.time_stamp, data.average))
            
            metrics.append (Metric_Type(item.name.localized_value,item.unit, times ))
    vm_metrics.append(VM_Metrics(vm, metrics))

print ("\nPerformance Metrics finished. Saving the data")


# Save to the directory
try:

    with open(FILENAME_METRICS, 'wb') as f:
        pickle.dump(vm_metrics, f, pickle.HIGHEST_PROTOCOL)

    with open(FILENAME_VMLIST, 'wb') as f:
        pickle.dump(vm_list, f, pickle.HIGHEST_PROTOCOL)
except:
    print (f"Error saving the files \"{FILENAME_METRICS}\" and \"{FILENAME_VMLIST}\". Do you have write access?")
    exit()
print (f"Saved successfully. The saved files are \"{FILENAME_METRICS}\" and \"{FILENAME_VMLIST}\"")