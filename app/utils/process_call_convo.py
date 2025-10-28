# app/api/routes/v1/process_calls/utils.py

import json
from typing import Optional, Literal
from openai import OpenAI


from app.core.config import api_keys_settings
from app.utils.extract_text_from_file import extract_text_from_file
from app.utils.language_map import LANGUAGE_MAP

from app.utils.logger_util import logger

# Set OpenAI API key from settings
client = OpenAI(api_key=api_keys_settings.OPENAI_API_KEY)



def generate_convocall_script(
    transcript_text: str,
    file_text: str,
    vendor_id: str,
    intent_id: str
) -> str:
    """
    Generate a conversational call flow script using GPT-4.
    
    Args:
        transcript_text: Transcript or context text
        file_text: Additional file content
        vendor_id: Vendor identifier
        intent_id: Intent identifier
    
    Returns:
        Generated call flow script as JSON string
    """
    # keep file_text available for prompt construction when needed

    if vendor_id == '1':
        prompt = f"""
            I am a senior recruiter making a phone call to a potential candidate. The goal is to check if the candidate is interested in a job opportunity, and if they are interested, 
            then only proceed to evaluate them using four pre-screening questions. These questions should include a mix of closed-ended and open-ended formats. One of the questions must be 
            open-ended to assess the candidate's communication skills, where the candidate is encouraged to speak for 15–20 seconds. 
            Please help me create a professional and engaging conversational flow between the recruiter and the candidate. 

            The flow should be structured in the following format with the proper headings for the recruiter to see the call script in a proper manner in JSON format with same titles  without fail like,
            Prompt
            Opening Layer
            Context of the Call
            Job Overview
            Pre-screening Questions
                Question
                Ideal Answer
            Call Ending Message

            Do not add much gap between the headings. Keep it minimalistic and then continue with below flow.
            1. Prompt - I am a senior recruiter making a phone call to a potential candidate. The goal is to check if the candidate is interested in a job opportunity, and if they are interested, 
            proceed to evaluate and screen them on few questions to check role fitment. You are a friendly assistant and never disconnect a call and know everything the user says. 
            In no situation you should disconnect the call unless call concludes, call concludes then disconnect by saying thanks, bye."
            (for voice agents calling context only, not to be read aloud during the call)

            2. Opening Layer - A friendly and professional greeting to initiate the call - Always keep the opening layer as " <break time="1s"/>Hi [Candidate's Name], this is [Your Name], 
            a senior recruiter AI assistant calling from [Your Company Name]. This call will be recorded for hiring purposes. Can I take a minute please & proceed?" 

            3. Context of the Call - Briefly explaining the purpose of the call and check if the person is interested in exploring job opportunity.

            4. Job Overview - A concise and compelling summary of the job opportunity. Limit the job overview to be spoken between 15-20 secs only.

            5. Pre-screening Questions - A total of four questions, including a mix of closed-ended and one open-ended question. Provide ideal answers (for internal evaluation only, 
            not to be read aloud during the call). Remove tags of "open ended" and "closed ended". Ask all close ended questions first and then open-ended questions. 
            On the phone call, do not say it is question one or two or three, directly start asking the question one, then wait for the candidate to answer then proceed to the next 
            question in the similar manner. 

            6. Call Ending Message - A polite and professional closing based on the candidate's interest level and responses. The goal is to keep the conversation natural, candidate-friendly, and
            aligned with a recruiter's tone while ensuring we gather the key information needed to assess suitability. Also, before ending do ask once if the candidate has any questions.

            To create a contextual conversational flow, you can also use the information provided here -

            "{transcript_text}" and "{file_text}"

            While sharing the call flow, do not add the initial summary of GPT response and the closing context of GPT response. Directly start with the opening layer and end with the call ending message.

            Always speak numbers in english (eg: 123 as one two three). Always speak country or city names in their full form (eg. AUS as Australia) except US and UK.

        """

    else:
        if intent_id == '13':
            Candidate_Name = "{{Candidate_Name}}"
            Your_Name = "{{Your_Name}}"
            Your_Company_Name = "{{Your_Company_Name}}"
            prompt = f"""
                You are communicating with a candidate via a phone call after they have accepted a job offer. You have access to the candidate's name and the company they are joining. The candidate may have questions or concerns about the background verification process.
                Your goal is to inform the candidate about the Background Verification process. Please help me create a professional and engaging conversational flow between the recruiter and the candidate. 

                The flow should be structured in the following format with the proper headings for the recruiter to see the call script in a proper manner in JSON format with same titles  without fail like,
                Prompt
                Your Role
                Rules to Follow
                Opening Layer
                Context of the Call
                Call Ending Message

                Do not add much gap between the headings. Keep it minimalistic and then continue with below flow.
                1. Prompt - You are communicating with a candidate via a phone call after they have accepted a job offer. Your goal is to inform the candidate about the Background Verification process. You have access to the candidate's name and the company they are joining. The candidate may have questions or concerns about the background verification process.

                2. Your Role - You are a Background Verification Assistant making a phone call to a candidate. Your goal is to inform the candidate about the Background Verification process. Answering any initial questions Candidate may have about the process . Mention that the user will receive an email with detailed instructions and a document checklist in the Context_of_the_Call section. You are a friendly, professional assistant and never disconnect a call unless the call concludes. At the end, you politely say: "Thanks, bye."

                3. Rules to Follow - Always provide simple, clear answers based only on available information. If unsure of question, respond with: "I am not too sure about the same right now, but I will ask someone from the team to assist you on the same." .Do not assume or generate information outside the provided data. Maintain a confident, warm, and professional tone – empathetic, clear, and engaging. Make the conversation feel natural and human, not rigid or robotic. Do not provide any information beyond the scope of the background verification process and onboarding. Always speak numbers in English words (e.g., 123 to one two three). Always use full country or city names (e.g., AUS to Australia), except US and UK.

                4. Opening Layer - Hi {Candidate_Name}, this is {Your_Name}, calling from {Your_Company_Name}. I'm calling in regards to your joining formalities. This call will be recorded for verification purpose. Can we proceed with the call?

                5. Context of the Call - First Congratulate the candidate on accepting the offer. Then Notifying Candidate that {Your_Company_Name} has initiated the background verification process.Explaining the importance of Candidate timely submission of required documents to expedite the process.Assuring Candidate that they will receive reminders to check the status of the background verification until it is completed.Then ask if candidate have any questions. (Pause for response)."

                6. Call Ending Message - Thank you for your time, {Candidate_Name}. Looking forward to you submitting the documents soon. Goodbye!

                To create a contextual conversational flow, you can also use the information provided here -

                "{transcript_text}" and "{file_text}" . if you find email id from this information provided then mention that they will receive an email shortly from this email id with detailed instructions and a document checklist in Context of the Call. Do not add any fake email_id only add that provided in information.

                While sharing the call flow, do not add the initial summary of GPT response and the closing context of GPT response. Directly start with the opening layer and end with the call ending message.

            """
        else:
            candidate_place = "{{Candidate_Name}}"
            your_name_place = "{{Your_Name}}"
            comapny_name_pace = "{{Your_Company_Name}}"

            json_resp = '{"Prompt":"","Opening Layer":"","Context of the Call":"","Job Overview":"","Pre-screening Questions":[{"Question":"","Ideal Answer":""},{"Question":"","Ideal Answer":""},{"Question":"","Ideal Answer":""},{"Question":"","Ideal Answer":""}],"Call Ending Message":""}'
            prompt = f"""
                I am a senior recruiter making a phone call to a potential candidate. The goal is to check if the candidate is interested in a job opportunity, and if they are interested, 
                then only proceed to evaluate them using four pre-screening questions. These questions should include a mix of closed-ended and open-ended formats. One of the questions must be 
                open-ended to assess the candidate's communication skills, where the candidate is encouraged to speak for 15–20 seconds. 
                Please help me create a professional and engaging conversational flow between the recruiter and the candidate. 

                The flow should be structured in the following format with the proper headings for the recruiter to see the call script in a proper manner in JSON format with same titles  without fail like,
                {json_resp}

                Do not add much gap between the headings. Keep it minimalistic and then continue with below flow.
                1. Prompt - I am a senior recruiter making a phone call to a potential candidate. The goal is to check if the candidate is interested in a job opportunity, and if they are interested, 
                proceed to evaluate and screen them on few questions to check role fitment. You are a friendly assistant and never disconnect a call and know everything the user says. 
                In no situation you should disconnect the call unless call concludes, call concludes then disconnect by saying thanks, bye."
                (for voice agents calling context only, not to be read aloud during the call)

                2. Opening Layer - A friendly and professional greeting to initiate the call - Always keep the opening layer as "Hi {candidate_place}, this is {your_name_place}, 
                a senior recruiter AI assistant calling from {comapny_name_pace}. This call will be recorded for hiring purposes. Can I take a minute please & proceed?" 

                3. Context of the Call - Briefly explaining the purpose of the call and check if the person is interested in exploring job opportunity.

                4. Job Overview - A concise and compelling summary of the job opportunity. Limit the job overview to be spoken between 15-20 secs only.

                5. Pre-screening Questions - A total of four questions, including a mix of closed-ended and one open-ended question. Provide ideal answers (for internal evaluation only, 
                not to be read aloud during the call). Remove tags of "open ended" and "closed ended". Ask all close ended questions first and then open-ended questions. 
                On the phone call, do not say it is question one or two or three, directly start asking the question one, then wait for the candidate to answer then proceed to the next 
                question in the similar manner. 

                6. Call Ending Message - A polite and professional closing based on the candidate's interest level and responses. The goal is to keep the conversation natural, candidate-friendly, and
                aligned with a recruiter's tone while ensuring we gather the key information needed to assess suitability. Also, before ending do ask once if the candidate has any questions.

                To create a contextual conversational flow, you can also use the information provided here -

                "{transcript_text}" and "{file_text}"

                While sharing the call flow, do not add the initial summary of GPT response and the closing context of GPT response. Directly start with the opening layer and end with the call ending message.

                Always speak numbers in english (eg: 123 as one two three). Always speak country or city names in their full form (eg. AUS as Australia) except US and UK.

            """
    
    response = client.chat.completions.create(
        model=api_keys_settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You have to give a conversation call flow"},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content or ""

def process_convocall(
    transcript_text: Optional[str],
    jdfile: Optional[str],
    env: str,
    vendor_id: str = "1",
    intent_id: str = "1",
    language_code: Literal["en", "pt", "es"] = "en"
) -> dict:
    """
    Main function to process convo call and generate script.
    """
    try:
        # Extract text from file if provided
        jdfile_text = ''
        if jdfile and len(jdfile) > 4:
            jdfile_text = extract_text_from_file(jdfile, env, 'jd')

        # Generate call script
        result = generate_convocall_script(
            transcript_text or "",
            jdfile_text,
            vendor_id,
            intent_id
        )

        # Clean the response
        final_response = (
            result.replace("json", "")
            .replace("```", "")
            .replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
        )

        # Parse JSON
        parsed = _normalize_pre_screening_sections(json.loads(final_response))
        cleaned = json.dumps(parsed, separators=(',', ':'))

        # Unified translation logic
        if language_code != 'en' and language_code in LANGUAGE_MAP:
            language_name = LANGUAGE_MAP[language_code]
            translate_prompt = f"""
            Data is "{cleaned}".
            You are given a JSON object. Your task is to translate only the values into {language_name} while keeping all the keys unchanged. Do not alter the structure, formatting, or order of the JSON.
            Return the result strictly as a JSON object with the same keys and translated values.
            """
            translation = client.chat.completions.create(
                model=api_keys_settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": f"You have to convert data into {language_name} Language"},
                    {"role": "user", "content": translate_prompt}
                ]
            )
            final_output = translation.choices[0].message.content or ""
            trim_json = (
                final_output.replace("json", "")
                .replace("```", "")
                .replace('\n', '')
                .replace('\r', '')
                .replace('\t', '')
            )
            trimmed_dict = _normalize_pre_screening_sections(json.loads(trim_json))
            logger.info(f"Successfully translated data to {language_name}: {json.dumps(trimmed_dict, ensure_ascii=False)}")
            return trimmed_dict
        else:
            return parsed

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise ValueError(f"Failed to parse response as JSON: {e}")
    except Exception as e:
        logger.error(f"Error processing convocall: {e}")
        raise

def _normalize_pre_screening_sections(payload: dict) -> dict:
    key = "Pre-screening Questions"
    if key not in payload:
        return payload
    questions = payload[key]
    if isinstance(questions, dict):
        ordered = [value for _, value in sorted(questions.items(), key=lambda item: item[0])]
        payload[key] = ordered
    elif not isinstance(questions, list):
        payload[key] = []
    return payload