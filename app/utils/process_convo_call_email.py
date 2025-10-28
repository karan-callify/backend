import json
from typing import Optional, Literal
from openai import OpenAI

from app.core.config import api_keys_settings
from app.utils.extract_text_from_file import extract_text_from_file
from app.utils.language_map import LANGUAGE_MAP

from app.utils.logger_util import logger

# Set OpenAI API key from settings
client = OpenAI(api_key=api_keys_settings.OPENAI_API_KEY)

def process_convocall_email(
    transcript_text: Optional[str],
    jdfile: Optional[str],
    env: str,
    vendor_id: str = "1",
    intent_id: str = "1",
    language_code: Literal["en", "pt", "es"] = "en"
) -> dict:
    """
    Main function to process convo call email and generate email content.
    """
    try:
        # Extract text from file if provided
        jdfile_text = ''
        if jdfile and len(jdfile) > 4:
            jdfile_text = extract_text_from_file(jdfile, env, 'jd')

        # Compose prompt based on intent
        if intent_id == "13":
            prompt = f"""
                Write a short, professional hiring email to a candidate (who accepted our offer) informing them that background verification has started and simply state they will receive an email shortly (ask them to check spam), emphasize timely submission, and include the company name in the subject line.
                Subject line of email should have [Company_Name] - Background Verification Process Initiated.
                Do not use this line or any relevant lines like “Hope you're doing well!”. The signature of email must contain only [Your_Name] & the [Company_Name]. When you start the email introduce who you are with your name and then get into the context. Limit the email to 150 words. Display the email in an attractive and professional form, and output should in JSON with subject and body keys only and nothing else. Use [Candidate_Name] for candidate name. Context is here - "{transcript_text}". if you find email id from Context mention that they will receive an email shortly from this email id with detailed instructions and a document checklist.
            """
        else:
            prompt = f"""
                I want to send an email to a candidate. It is kind of notifying the candidate that you will receive a digital call at [Time] on [Date]. The email has details about the context and it also mentions a [Pre_Apply] which when clicked, candidates can pre apply as an alternative to the call. Subject line of email should have [Company_Name], role and location if mentioned. Do not use this line or any relevant lines like “Hope you're doing well!”. The signature of email must contain only [Your_Name] & the [Company_Name]. When you start the email introduce who you are with your name and then get into the context. Limit the email to 150 words. Display the email in an attractive and professional form, and output should in JSON with subject and body keys only and nothing else. Use [Candidate_Name] for candidate name. Context is here - "{transcript_text}" and "{jdfile_text}"
            """

        response = client.chat.completions.create(
            model=api_keys_settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You have to give a conversation call flow"},
                {"role": "user", "content": prompt}
            ]
        )

        result = response.choices[0].message.content or ""
        # Clean the response
        final_response = (
            result.replace("json", "")
            .replace("```", "")
            .replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
        )

        # Parse JSON
        parsed = json.loads(final_response)
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
            return json.loads(trim_json)
        else:
            return json.loads(cleaned)

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        raise ValueError(f"Failed to parse response as JSON: {e}")
    except Exception as e:
        logger.error(f"Error processing convocall email: {e}")
        raise


