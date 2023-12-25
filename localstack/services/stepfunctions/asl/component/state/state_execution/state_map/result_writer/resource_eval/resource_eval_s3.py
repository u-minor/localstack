from __future__ import annotations

import json
from typing import Callable, Final

from localstack.services.stepfunctions.asl.component.state.state_execution.state_map.result_writer.resource_eval.resource_eval import (
    ResourceEval,
)
from localstack.services.stepfunctions.asl.component.state.state_execution.state_task.service.resource import (
    ResourceRuntimePart,
)
from localstack.services.stepfunctions.asl.eval.environment import Environment
from localstack.services.stepfunctions.asl.utils.boto_client import boto_client_for
from localstack.utils.strings import camel_to_snake_case


class ResourceEvalS3(ResourceEval):
    _HANDLER_REFLECTION_PREFIX: Final[str] = "_handle_"
    _API_ACTION_HANDLER_TYPE = Callable[[Environment, ResourceRuntimePart], None]

    @staticmethod
    def _get_s3_client(resource_runtime_part: ResourceRuntimePart):
        return boto_client_for(
            region=resource_runtime_part.region,
            account=resource_runtime_part.account,
            service="s3",
        )

    @staticmethod
    def _handle_put_object(env: Environment, resource_runtime_part: ResourceRuntimePart) -> None:
        s3_client = ResourceEvalS3._get_s3_client(resource_runtime_part=resource_runtime_part)
        parameters = env.stack.pop()
        results = env.stack.pop()
        map_run_record = env.map_run_record_pool_manager.get_all().pop()

        succeeded = [
            {
                "ExecutionArn": "",
                "Input": '"alpha"',
                "InputDetails": {"Included": True},
                "Name": "",
                "Output": result["body"],
                "OutputDetails": {"Included": True},
                "StartDate": map_run_record.start_date.isoformat(),
                "StateMachineArn": env.context_object_manager.context_object["StateMachine"]["Id"],
                "Status": map_run_record.status,
                "StopDate": map_run_record.stop_date.isoformat(),
            }
            for result in results
            if result["statusCode"] == 200
        ]

        body = {
            "DestinationBucket": parameters["Bucket"],
            "MapRunArn": map_run_record.map_run_arn,
            "ResultFiles": {"FAILED": [], "PENDING": [], "SUCCEEDED": succeeded},
        }
        uuid = map_run_record.map_run_arn.split(":")[-1]
        key = parameters["Prefix"] + uuid + "/manifest.json"
        s3_client.put_object(
            Bucket=parameters["Bucket"], Key=key, Body=json.dumps(body, indent=2).encode("utf8")
        )
        env.stack.append(
            {
                "MapRunArn": map_run_record.map_run_arn,
                "ResultWriterDetails": {"Bucket": parameters["Bucket"], "Key": key},
            }
        )

    def _get_api_action_handler(self) -> ResourceEvalS3._API_ACTION_HANDLER_TYPE:
        api_action = camel_to_snake_case(self.resource.api_action).strip()
        handler_name = ResourceEvalS3._HANDLER_REFLECTION_PREFIX + api_action
        resolver_handler = getattr(self, handler_name)
        if resolver_handler is None:
            raise ValueError(f"Unknown s3 action '{api_action}'.")
        return resolver_handler

    def eval_resource(self, env: Environment) -> None:
        self.resource.eval(env=env)
        resource_runtime_part: ResourceRuntimePart = env.stack.pop()
        resolver_handler = self._get_api_action_handler()
        resolver_handler(env, resource_runtime_part)
