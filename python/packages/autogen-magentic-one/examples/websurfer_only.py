"""This example demonstrates MagenticOne performing a task given by the user and returning a final answer."""

import argparse
import asyncio
import logging
import os
import json

from autogen_core import EVENT_LOGGER_NAME, AgentId, AgentProxy, SingleThreadedAgentRuntime
from autogen_core.code_executor import CodeBlock
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
# from autogen_magentic_one.agents.coder import Coder, Executor
# from autogen_magentic_one.agents.file_surfer import FileSurfer
from autogen_magentic_one.agents.multimodal_web_surfer import MultimodalWebSurfer
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env

from datetime import datetime
from autogen_magentic_one.queries.queries import generate_query_and_instructions


# NOTE: Don't forget to 'playwright install --with-deps chromium'
from dotenv import load_dotenv
load_dotenv()

CHAT_COMPLETION_PROVIDER = os.getenv("CHAT_COMPLETION_PROVIDER")
CHAT_COMPLETION_KWARGS_JSON = os.getenv("CHAT_COMPLETION_KWARGS_JSON")

def generate_folder_name(difficulty: str, id_query: int) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if id_query < 10:
        id_query_folder_name = f"0{id_query}"
    else:
        id_query_folder_name = id_query
    return f"vision_magnetic_{difficulty}_{id_query_folder_name}_{timestamp}" 


async def confirm_code(code: CodeBlock) -> bool:
    response = await asyncio.to_thread(
        input,
        f"Executor is about to execute code (lang: {code.language}):\n{code.code}\n\nDo you want to proceed? (yes/no): ",
    )
    return response.lower() == "yes"
###
async def main(logs_dir: str, hil_mode: bool, save_screenshots: bool, difficulty: str, id_query: int, query_num_listings: int, query_num_websites: int) -> None:
    # logs_dir is now the dynamically created subfolder (log_folder)
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model="gpt-4o")

    async with DockerCommandLineCodeExecutor(work_dir=logs_dir) as code_executor:
        # Register agents and pass the correct log folder
        # await Coder.register(runtime, "Coder", lambda: Coder(model_client=client))
        # coder = AgentProxy(AgentId("Coder", "default"), runtime)

        # await Executor.register(
        #     runtime,
        #     "Executor",
        #     lambda: Executor("A agent for executing code", executor=code_executor, confirm_execution=confirm_code),
        # )
        # executor = AgentProxy(AgentId("Executor", "default"), runtime)

        await MultimodalWebSurfer.register(runtime, "WebSurfer", MultimodalWebSurfer)
        web_surfer = AgentProxy(AgentId("WebSurfer", "default"), runtime)

        await UserProxy.register(
            runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

        agent_list = [web_surfer,
                    #   coder,
                    #   executor
        ]

        if hil_mode:
            agent_list.append(user_proxy)

        await LedgerOrchestrator.register(
            runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=client,
                max_rounds=30,
                max_time=25 * 60,
                return_final_answer=True,
            ),
        )

        runtime.start()

        # Initialize the web surfer agent with the correct folder
        actual_surfer = await runtime.try_get_underlying_agent_instance(web_surfer.id, type=MultimodalWebSurfer)
        await actual_surfer.init(
            model_client=client,
            downloads_folder=logs_dir,  # Pass the log_folder here
            start_page="https://www.google.com", #TODO: define starting page here; create as passed argument..
            browser_channel="chromium",
            headless=True,
            debug_dir=logs_dir,  # Pass the log_folder here
            to_save_screenshots=save_screenshots,
        )

        await runtime.send_message(RequestReplyMessage(), user_proxy.id)
        await runtime.stop_when_idle()



def none_or_int(value: str):
    if value.lower() == "none":  # Check for the string "none" (case-insensitive)
        return None
    return int(value)  # Convert to int if it's not "none"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MagenticOne example with log directory.")
    parser.add_argument("--logs_dir", type=str, required=True, help="Directory to store log files and downloads")
    parser.add_argument("--hil_mode", action="store_true", default=False, help="Run in human-in-the-loop mode")
    parser.add_argument(
        "--save_screenshots", action="store_true", default=False, help="Save additional browser screenshots to file"
    )
    parser.add_argument("--difficulty", type=str, required=False, help="Difficulty level for query")
    parser.add_argument("--id_query", type=int, required=False, help="ID of the predefined query")
    parser.add_argument("--query_num_listings", type=none_or_int, required=False, help="Number of listings to query (or None)")
    parser.add_argument("--query_num_websites", type=none_or_int, required=False, help="Number of websites to query (or None)")

    args = parser.parse_args()

    # Validate difficulty and id_query
    difficulty = args.difficulty if args.difficulty else input("Enter difficulty level: ")
    # if difficulty not in queries_no_formatting_instructions:
    #     raise ValueError(f"Invalid difficulty level: {difficulty}. Available: {list(queries_no_formatting_instructions.keys())}")

    # Default to 0 if id_query not provided, and validate
    id_query = args.id_query if args.id_query is not None else 0
    # available_queries = queries_no_formatting_instructions[difficulty]
    # if not (0 <= id_query < len(available_queries)):
    #     raise ValueError(f"Invalid id_query: {id_query}. Available IDs for difficulty '{difficulty}': {list(range(len(available_queries)))}")

    # Generate query automatically
    query_num_listings = args.query_num_listings
    query_num_websites = args.query_num_websites

    query = generate_query_and_instructions(query_num_listings=query_num_listings, query_num_websites=query_num_websites, difficulty=difficulty, id_query=id_query)

    print(f"Generated Query: {query}\n")

    # Generate the subfolder name and ensure it exists
    folder_name = generate_folder_name(difficulty, id_query)
    log_folder = os.path.join(args.logs_dir, folder_name)
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    log_file_path = os.path.join(log_folder, "log.jsonl")

    # Write arguments and query to the log file before logging starts
    with open(log_file_path, "w") as log_file:
        initial_log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "Initialization",
            "arguments": {
                "logs_dir": args.logs_dir,
                "hil_mode": args.hil_mode,
                "save_screenshots": args.save_screenshots,
                "folder_name": log_folder,
                "difficulty": difficulty,
                "id_query": id_query,
                "query_num_listings": query_num_listings,
                "query_num_websites": query_num_websites,
            },
            "query": query,
        }
        log_file.write(f"{json.dumps(initial_log_entry)}\n")

    # Update the logger to use the correct log folder
    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler(filename=os.path.join(log_folder, "log.jsonl"))
    logger.handlers = [log_handler]

    # Pass log_folder (not logs_dir) to the main function
    asyncio.run(main(log_folder, args.hil_mode, args.save_screenshots, difficulty, id_query, query_num_listings, query_num_websites))

""" 
python examples/websurfer_only.py --logs_dir ./logs/ --save_screenshots --difficulty advanced --id_query 2 --query_num_listings None --query_num_websites None

python examples/websurfer_only.py --logs_dir ./logs/ --save_screenshots --difficulty easy --id_query 0 --query_num_listings None --query_num_websites None


"""