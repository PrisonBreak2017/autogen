import autogen

config_list = [
    {
        "api_base": "http://152.32.148.19:3000/v1",
        "model": "gpt-3.5-turbo-16k",
        "api_key": "sk-5Zr8mdQ2UN7zpzEx9301B328F3224496B0E641BfDf9957C2",
        "timeout": 300
    }
]

def ask_expert(message):
    assistant_for_expert = autogen.AssistantAgent(
        name="assistant_for_expert",
        llm_config={
            "temperature": 0,
            "config_list": config_list,
        },
    )
    expert = autogen.UserProxyAgent(
        name="expert",
        human_input_mode="ALWAYS",
        code_execution_config={"work_dir": "expert"},
    )

    expert.initiate_chat(assistant_for_expert, message=message)
    expert.stop_reply_at_receive(assistant_for_expert)
    # expert.human_input_mode, expert.max_consecutive_auto_reply = "NEVER", 0
    # final message sent from the expert
    expert.send("summarize the solution and explain the answer in an easy-to-understand way", assistant_for_expert)
    # return the last message the expert received
    return expert.last_message()["content"]


assistant_for_student = autogen.AssistantAgent(
    name="assistant_for_student",
    system_message="You are a helpful assistant. Reply TERMINATE when the task is done.",
    llm_config={
        "request_timeout": 600,
        "seed": 42,
        # Excluding azure openai endpoints from the config list.
        # Change to `exclude="openai"` to exclude openai endpoints, or remove the `exclude` argument to include both.
        "config_list":config_list,
        "model": "gpt-3.5-turbo",  # make sure the endpoint you use supports the model
        "temperature": 0,
        "functions": [
            {
                "name": "ask_expert",
                "description": "ask expert when you can't solve the problem satisfactorily.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "question to ask expert. Ensure the question includes enough context, such as the code and the execution result. The expert does not know the conversation between you and the user unless you share the conversation with the expert.",
                        },
                    },
                    "required": ["message"],
                },
            }
        ],
    }
)

student = autogen.UserProxyAgent(
    name="student",
    human_input_mode="TERMINATE",
    
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "student"},
    function_map={"ask_expert": ask_expert},
)

# the assistant receives a message from the student, which contains the task description
student.initiate_chat(
    assistant_for_student,
    message="""Find $a + b + c$, given that $x+y \\neq -1$ and 
\\begin{align}
	ax + by + c & = x + 7,\\
	a + bx + cy & = 2x + 6y,\\
	ay + b + cx & = 4x + y.
\\end{align}.
""",
)