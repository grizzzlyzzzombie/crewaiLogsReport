import os

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, DirectoryReadTool, FileReadTool
from langchain_openai import AzureChatOpenAI

from tools.report_sender_tool import SendEmailTool

# os.environ["OPENAI_API_BASE"] = 'secret'
# os.environ["OPENAI_MODEL_NAME"] = 'secret'
# os.environ["OPENAI_API_KEY"] = "secret"
# os.environ["OPENAI_API_KEY"] = "secret"
# os.environ["OPENAI_MODEL_NAME"] = 'secret'
os.environ["OPENAI_API_VERSION"] = 'secret'

os.environ["SERPER_API_KEY"] = "secret"

os.environ["AZURE_OPENAI_VERSION"] = "secret"
os.environ["AZURE_OPENAI_DEPLOYMENT"] = "secret"
os.environ[
    "AZURE_OPENAI_ENDPOINT"] = "secret"
os.environ["AZURE_OPENAI_KEY"] = "secret"

azure_llm = AzureChatOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_KEY"),
    api_version="secret"
)

directory_reader = DirectoryReadTool()
serper_tool = SerperDevTool()
file_read_tool = FileReadTool()
send_email_tool = SendEmailTool()

latest_founder_agent = Agent(
    role="File Reader Agent",
    goal="Read file names in a directory and find the newest files by date."
         " Try to analyze name patterns to find similar files and latest files. Date is in file name like:"
         "import_internet_speed_04032024: import_internet_speed - mame pf job, 04032024 - date in dd:mm:yyyy",
    backstory=(
        "You are a meticulous file reader with a keen eye for detail. "
        "Your job is to identify the most recent files in a given directory."
    ),
    memory=True,
    tools=[directory_reader],
    allow_delegation=False,
    verbose=True,
    llm=azure_llm
)

log_analyzer_agent = Agent(
    role="Senior Log Analysis Specialist",
    goal="To ensure the integrity, performance, and reliability of IT systems by meticulously analyzing "
         "and interpreting system logs, identifying issues, and providing actionable insights.",
    backstory=(
        "You are expert with over 15 years of experience in the IT industry, "
        "is a seasoned expert in log analysis and system monitoring."
        "Holding a Master's degree in Computer Science, "
        "Renowned for the ability to quickly decipher complex logs,"
        "Known for a methodical approach and sharp analytical mind, you are dedicated to ensuring"
        "seamless operations and upholding the highest standards of system reliability."
    ),
    memory=True,
    tools=[file_read_tool],
    allow_delegation=False,
    verbose=True,
    llm=azure_llm
)

email_agent = Agent(
    llm=azure_llm,
    role="Secretary for emails",
    goal="Formulate a email body with report data. ONLY BODY IS REQUIRED",
    backstory=(
        "You are the master in writing emails with reports from provided data"
    ),
    memory=True,
    verbose=True,
    tools=[send_email_tool],
    allow_delegation=True
)

find_latest_task = Task(
    llm=azure_llm,
    agent=latest_founder_agent,
    description=(
        "Read the file names in {logs_directory} and find the newest files by date for each type of job or system part."
        "Provide a list of these files."
    ),
    expected_output='Array of file paths',
    tools=[directory_reader]
)

analyze_logs_task = Task(
    llm=azure_llm,
    agent=log_analyzer_agent,
    description=(
        "Analyze logs from provided from context to formulate table about current state of system."
    ),
    expected_output=(
        'Make separate table for each import jobs amd microservices'
        'For import jobs: type of coverage, name of table, environment, time spent for operation'
        'For microservice: error, exception type, exception message'
    ),
    output_file="./report.md",
    context=[find_latest_task],
    tools=[file_read_tool],
    verbose=True
)

send_report_task = Task(
    llm=azure_llm,
    agent=email_agent,
    description=(
        "This task provides necessary tools and agent for creating report from analyzed logs"
    ),
    expected_output=(
        'Data is successfully send to team email'
    ),
    context=[analyze_logs_task],
    tools=[send_email_tool],
)

crew = Crew(
    agents=[log_analyzer_agent],
    tasks=[find_latest_task, analyze_logs_task, send_report_task],
    process=Process.sequential
)

inputs = {'logs_directory': './logs'}
result = crew.kickoff(inputs)
print(result)
