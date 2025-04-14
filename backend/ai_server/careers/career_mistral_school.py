from dotenv import load_dotenv
from common.logging.logger import get_gpt_logger
from common.db.db_helper import insert_career, insert_steps, update_step, add_careers, update_career_status, \
    update_token_usage
import asyncio
import os

from mistralai.async_client import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage



async def find_career(data):
    careerData = {}
    try:
        userId = data['userId']
        careerData = data['careerData']
        log = get_gpt_logger()
        log.debug('Finding careers for user =%s, career_data=%s', userId, careerData)
        responseData = {}
        projectFolder = os.path.expanduser('../..')
        load_dotenv(os.path.join(projectFolder, '.env'))
        mistralAPIKey = os.getenv('MISTRAL_API_KEY')
        mistralModel = os.getenv('MISTRAL_AI_MODEL')
        client = MistralAsyncClient(api_key=mistralAPIKey)

        # Fetch career option for career 1
        qualification = careerData['qualification']  # "MBA or BE Electrical"
        allCareerStreams = qualification

        personalityTrait1 = careerData['personalityTrait1']  # "Openness"
        personalityTrait2 = careerData['personalityTrait2']  # "Agreeableness"
        careerInterest1 = careerData['careerInterest1']  # "Social"
        careerInterest2 = careerData['careerInterest2']  # "Conventional"
        message = """        
        Based on a student's top 2 personality traits from the Big
        5 personality test and their top 2 career interest types
        from the RIASEC career interest assessment, generate 10
        aspiring, fulfilling, and emerging career options suitable
        for an %s-grade student in India.
        Input:
        -Personality Traits (Big 5):
            - %s
            - %s
       
        -Career Interests (RIASEC):
            - %s
            - %s
        Output: Provide a list of 10 career options that align with
        the given personality traits and career interests. For each
        career option, include a brief explanation of why it suits
        the student's strengths and interests.
            """% (allCareerStreams, personalityTrait1, personalityTrait2, careerInterest1, careerInterest2)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=message)],
                                 )
        careerOptions = chat.choices[0].message.content
        log.debug('inserting career for user=%s', userId)

        allCareers = allCareerStreams + "====" + careerOptions
        # add career information in generated careers
        add_careers(userId, allCareerStreams, personalityTrait1, personalityTrait2, careerInterest1, careerInterest2,
                    careerOptions)
        insert_career(userId, allCareers)

        responseData['message'] = "Career searched"
        responseData['status_code'] = 200
        return responseData
    except Exception as error:
        log.error('Error in search career for =%s', careerData, exc_info=True)
        raise error

async def find_career_steps(data):
    try:
        userId = data['userId']
        careerTitle = data['careerTitle']
        qualification = data['qualification']
        log = get_gpt_logger()
        log.debug('Finding career steps for user =%s, career_title=%s', userId, careerTitle)
        responseData = {}

        project_folder = os.path.expanduser('../..')
        load_dotenv(os.path.join(project_folder, '.env'))
        mistralAPIKey = os.getenv('MISTRAL_API_KEY')
        mistralModel = os.getenv('MISTRAL_AI_MODEL')
        careerTitle = careerTitle.strip()
        client = MistralAsyncClient(api_key=mistralAPIKey)

        step0question =  """
        Provide concise first-person guidance for an %s-grade student
        about the career option of %s.
        Include the following details:
        1. Explain the Role:
        -Briefly describe what a %s does, highlighting key
        responsibilities and typical tasks.
        2. Alignment with Personality and Career Interests:
        - Explain how the role of %s aligns with the student's
        personality traits (high openness to experiences and high
        neuroticism) and career interests (realistic and artistic).
        3. Job Opportunities:
        - Mention local and global job opportunities for %s,
        including industries and sectors where these professionals are in
        demand.
        4. Future Trends:
        - Highlight key future trends in the field of %s,
        including emerging technologies or methodologies that may
        impact the role.
        5. Aspiring Career Tagline:
        - Provide an inspiring tagline or motto that encapsulates the
        essence of pursuing a career as a %s.
        Output Format:
        - Present the information in a conversational and engaging first-person
        narrative, as if speaking directly to the student.
        - Use clear headings to organize the information for easy understanding.
        Example Output Structure:
        Your Journey to Becoming an %s
        What is an %s?
        [Brief description of the role and responsibilities]
        Why %s is Perfect for You:
        [Explanation of alignment with personality and interests]
        Exciting Job Opportunities:
        [Information on local and global job opportunities]
        Future Trends in %s:
        [Discussion of future trends and their impact]
        Your Inspiring Career Tagline:
        [Inspiring tagline or motto]
        """ % (qualification, careerTitle, careerTitle,careerTitle, careerTitle,careerTitle, careerTitle,careerTitle, careerTitle,careerTitle,careerTitle)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step0question)], )
        careerSteps0 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 0 for {careerTitle}-: {careerSteps0}")
        update_step(careerTitle, qualification, 'step_0', careerSteps0)

        step1question = """
        Provide detailed guidance for an %sth-grade student on the aptitudes
        and abilities required to pursue a career as a %s.
        Include the following details:
        1. Aptitudes to Build:
        - List the key aptitudes required for %s, such as
        Language Aptitude, Abstract Reasoning, Verbal Reasoning,
        Mechanical Reasoning, Numerical Aptitude, Spatial Aptitude, and
        Perceptual Aptitude.
        - Explain why each aptitude is important for the role.
        - Suggest activities and strategies to build these aptitudes during
        schooling years, including specific subjects to focus on,
        extracurricular activities, and projects.
        - Provide resources like online tests and assessments to evaluate
        these aptitudes (e.g., websites or apps for aptitude testing).
        2. Abilities Required:
        - Identify the essential abilities needed to perform well as a
        %s, such as creativity, problem-solving,
        communication skills, etc.
        - Explain how each ability contributes to success in the role.
        - Suggest ways to start developing these abilities during schooling
        years, including participation in relevant clubs, competitions, and
        projects.
        - Provide resources like online courses or tutorials to help build
        these abilities (e.g., platforms offering courses related to the
        career).
        Output Format:
        - Present the information in a clear and structured manner, using
        headings and bullet points for easy understanding.
        - Ensure the guidance is actionable and tailored to the student's current
        educational level.
        Example Output Structure:
        Building Your Skills for a Career as an %s
        Key Aptitudes to Develop:
        - [List of aptitudes and their importance]
        - [Activities and strategies to build each aptitude]
        - [Resources for aptitude assessment]
        Essential Abilities for Success:
        - [List of abilities and their significance]
        - [Ways to develop each ability during schooling years]
        - [Resources for ability development]
        """ % (qualification, careerTitle,careerTitle,careerTitle,careerTitle)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step1question)], )
        careerSteps1 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 1 for {careerTitle}-: {careerSteps1}")
        update_step(careerTitle, qualification, 'step_1', careerSteps1)

        step2question = """
        You are a career counselor providing personalized guidance to a %sth-grade
        student for the %s career option, generate a detailed response covering the following aspects. Ensure the tone is friendly,
        supportive, and tailored to a %sth-grade student's understanding.
        1. Stream and Subject Selection:
        - Suggest subjects aligned with the recommended career option
        for the 11th and 12th grades.
        - Consider the new education policy (NEP) while making these
        suggestions.
        2. Extracurricular Activities:
        
        Recommend activities related to the student's interests, such as
        clubs, internships, and workshops, that they can participate in
        during their 11th and 12th grades.
        3. Career Awareness and Research:
        - Suggest what research the student should conduct for the
        selected career option.
        - Provide guidance on how to gather more information and
        prepare for this career path.
        Output Format:
        Stream and Subject Selection:
        [Your suggestions for subjects aligned with the career option, considering
        NEP]Extracurricular Activities:
        [Your recommendations for clubs, internships, workshops, etc.]
        Career Awareness and Research:
        [Your suggestions for research and preparation for the career option]
         """ % (qualification, careerTitle,qualification)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step2question)], )
        careerSteps2 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 2 for {careerTitle}-: {careerSteps2}")
        update_step(careerTitle, qualification, 'step_2', careerSteps2)

        step3question = """
        You are a career counselor providing personalized guidance to an %sth-grade student for a %s career option. Generate a detailed response covering the following aspects. Ensure the tone is friendly, supportive, and tailored to an %sth-grade student's understanding.
        Entrance Exams for Higher Education:
        List the entrance exams relevant to the selected career option for undergraduate studies in India.
        Provide a brief description of each exam.
        Preparation for Entrance Exams:
        Suggest strategies and resources for preparing for these entrance exams.
        Include tips on study materials, coaching options, and practice tests.
        Top Institutions in India:
        List the top 10 reputable institutions in India for the selected career option.
        Provide links to their websites.
        Include an indicative fee structure and yearly cost for undergraduate studies.
        Mention that these are indicative numbers and may change, advising students to check the latest information on the institutions' websites.
        Top Institutions Abroad:
        List the top 10 reputable institutions abroad for the selected career option.
        Provide links to their websites.
        Include an indicative fee structure and yearly cost for undergraduate studies.
        Mention that these are indicative numbers and may change, advising students to check the latest information on the institutions' websites.
        Output Format:

        Entrance Exams for Higher Education:
        [Exam Name 1]
        Description: [Brief description of the exam]
        [Exam Name 2]
        Description: [Brief description of the exam]
        ...
        Preparation for Entrance Exams:
        .
        .
        .
        Top Institutions in India:
        [Institution Name 1]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]
        [Institution Name 2]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]
        ...
        Top Institutions Abroad:
        [Institution Name 1]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]
        [Institution Name 2]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]

        """ % (qualification, careerTitle,qualification)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step3question)], )
        careerSteps3 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 3 for {careerTitle}-: {career_steps3}")
        update_step(careerTitle, qualification, 'step_3', careerSteps3)

        step4question = """
        You are a career counselor providing personalized guidance to an %sth-grade student for a %s career option. Generate a detailed response covering the following aspects for postgraduate studies. Ensure the tone is friendly, supportive, and tailored to an %sth-grade student's understanding.
        Entrance Exams for Higher Education:
        List the entrance exams relevant to the selected career option for postgraduate studies in India.
        Provide a brief description of each exam.
        Preparation for Entrance Exams:
        Suggest strategies and resources for preparing for these entrance exams.
        Include tips on study materials, coaching options, and practice tests.
        Top Institutions in India:
        List the top 10 reputable institutions in India for the selected career option.
        Provide links to their websites.
        Include an indicative fee structure and yearly cost for postgraduate studies.
        Mention that these are indicative numbers and may change, advising students to check the latest information on the institutions' websites.
        Top Institutions Abroad:
        List the top 10 reputable institutions abroad for the selected career option.
        Provide links to their websites.
        Include an indicative fee structure and yearly cost for postgraduate studies.
        Mention that these are indicative numbers and may change, advising students to check the latest information on the institutions' websites.
        Output Format:

        Entrance Exams for Higher Education:
        [Exam Name 1]
        Description: [Brief description of the exam]
        [Exam Name 2]
        Description: [Brief description of the exam]
        ...
        Preparation for Entrance Exams:
        .
        .
        .
        Top Institutions in India:
        [Institution Name 1]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]
        [Institution Name 2]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]
        ...
        Top Institutions Abroad:
        [Institution Name 1]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]
        [Institution Name 2]
        Website: [Link to website]
        Indicative Fee Structure: [Indicative fee and yearly cost]

        """ % (qualification, careerTitle,qualification)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step4question)], )
        careerSteps4 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 4 for {careerTitle}-: {career_steps4}")
        update_step(careerTitle, qualification, 'step_4', careerSteps4)

        step5question = """
        You are a career counselor providing personalized guidance to an %sth-grade student for a %s career option. Generate a detailed response covering the following aspects of skill development and networking during and after higher education. Ensure the tone is friendly, supportive, and tailored to an %sth-grade student's understanding.
        Internships:
        Explain the importance of gaining practical experience through internships or summer programs.
        Suggest how to find and apply for internships.
        Skill Enhancement:
        Recommend additional skills related to the chosen field.
        Suggest courses, certifications, and workshops to enhance these skills.
        Type of Role:
        Describe the type of role the student can expect to enter into this field.
        Entry-Level Salary:
        Provide an indicative entry-level salary range in India for the chosen career.
        Organizations Offering Internships:
        List organizations or businesses that offer internship roles in this chosen field in India and abroad.
        Networking:
        Explain the importance of networking in the industry.
        Suggest ways to connect with professionals, mentors, and alumni.
        Output Format:

        Internships:
        Importance: [Explanation of why internships are important]
        How to Find and Apply: [Tips on finding and applying for internships]
        Skill Enhancement:
        Additional Skills: [List of additional skills related to the chosen field]
        Courses and Certifications: [Recommended courses, certifications, and workshops]
        Type of Role:
        Description: [Description of the entry-level role]
        Entry-Level Salary:
        Indicative Range: [Indicative entry-level salary range in India]
        Organizations Offering Internships:
        In India:
        [Organization Name 1]
        [Organization Name 2] ...
        Abroad:
        [Organization Name 1]
        [Organization Name 2] ...
        Networking:
        Importance: [Explanation of why networking is important]
        How to Connect: [Tips on connecting with professionals, mentors, and alumni]

        """ % (qualification, careerTitle,qualification)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step5question)], )
        careerSteps5 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 5 for {careerTitle}-: {career_steps5}")
        update_step(careerTitle, qualification, 'step_5', careerSteps5)

        step6question = """
        You are a career counselor providing personalized guidance to an %sth-grade student for the next steps after their studies, focusing on entering the workforce for a %s career option. Generate a detailed response covering the following aspects. Ensure the tone is friendly, supportive, and tailored to an 8th to %sth-grade student's understanding.
        Entry-Level Jobs:
        Describe the types of entry-level jobs available for the chosen career option.
        Provide a brief overview of what these roles entail.
        Salaries in India:
        Provide an indicative range of entry-level salaries in India for the chosen career option.
        Mention that these are indicative numbers and may change, advising students to check the latest information.
        Tips on Career Progression:
        Offer tips on how to progress in the chosen career, including skills to develop, certifications to pursue, and strategies for advancement.
        Companies Offering Relevant Roles:
        List a few companies in India that offer roles relevant to the chosen career option.
        Provide a brief description of each company.
        Output Format:

        Entry-Level Jobs:
        Job Title 1: [Brief description of the role]
        Job Title 2: [Brief description of the role]
        Job Title 3: [Brief description of the role]
        Salaries in India:
        Indicative Range: [Indicative entry-level salary range in India]
        Note: These are indicative numbers and may change. Please check the latest information.
        Tips on Career Progression:
        Skill Development: [Suggestions on skills to develop]
        Certifications: [Recommended certifications to pursue]
        Strategies for Advancement: [Tips on how to advance in the career]
        Companies Offering Relevant Roles:
        [Company Name 1]: [Brief description of the company]
        [Company Name 2]: [Brief description of the company]
        [Company Name 3]: [Brief description of the company]

        """ % (qualification, careerTitle,qualification)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step6question)], )
        careerSteps6 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 6 for {careerTitle}-: {career_steps6}")
        update_step(careerTitle, qualification, 'step_6', careerSteps6)

        step7question = """
        You are a career counselor providing guidance to an %sth-grade student on continuous learning and development as they enter the workforce for a %s career option. Generate a detailed response covering the following aspects. Ensure the tone is friendly, supportive, and tailored to an %sth-grade student's understanding.

        Skill Enhancement:

        Explain the importance of continuously upgrading skills to adapt to industry changes.
        Suggest ways to enhance both technical and soft skills.
        Recommend resources and strategies for continuous learning.
        Career Advancement:

        Provide tips on aiming for promotions and leadership roles.
        Suggest strategies for specialization within the chosen career field.
        Offer advice on setting career goals and tracking progress.
        Output Format:

        Skill Enhancement:

        Importance: [Explanation of why continuous skill enhancement is important]
        Technical Skills: [Suggestions on how to upgrade technical skills]
        Soft Skills: [Suggestions on how to enhance soft skills]
        Resources and Strategies: [Recommended resources and strategies for continuous learning]
        Career Advancement:

        Aiming for Promotions: [Tips on how to aim for promotions]
        Leadership Roles: [Strategies for taking on leadership roles]
        Specialization: [Suggestions for specializing within the career field]
        Setting Career Goals: [Advice on setting and tracking career goals]
        """% (qualification, careerTitle,qualification)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step7question)], )
        careerSteps7 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 7 for {careerTitle}-: {career_steps7}")
        update_step(careerTitle, qualification, 'step_7', careerSteps7)

        step8question = """
        You are a career counsellor providing a comprehensive summary of guidance to an %sth-grade student for a %s career option. Generate a detailed response that covers all aspects from the introduction to the career path up to becoming a successful professional. Ensure the tone is friendly, supportive, and tailored to an %sth-grade student's understanding. Include a congratulatory note and best wishes for their career.
        Output Format:

        Introduction to %s:
        Brief Overview: [A brief introduction to the career option]
        Stream and Subject Selection (11th and 12th Grade):
        Recommended Stream: [Suggested stream aligned with the career option]
        Subjects: [List of subjects to consider, keeping NEP in mind]
        Extracurricular Activities (11th and 12th Grade):
        Clubs and Internships: [Recommended clubs, internships, and workshops]
        Career Awareness and Research:
        Research Topics: [What research should be done for the selected career option]
        Preparation for Undergraduate Studies:
        Entrance Exams: [List of entrance exams for undergraduate studies in India]
        Preparation Tips: [Strategies and resources for preparing for these exams]
        Top Institutions in India for Undergraduate Studies:
        [Institution Name 1]: [Brief description, website link, indicative fee structure]
        [Institution Name 2]: [Brief description, website link, indicative fee structure]
        Top Institutions Abroad for Undergraduate Studies:
        [Institution Name 1]: [Brief description, website link, indicative fee structure]
        [Institution Name 2]: [Brief description, website link, indicative fee structure]
        Preparation for Postgraduate Studies:
        Entrance Exams: [List of entrance exams for postgraduate studies in India]
        Preparation Tips: [Strategies and resources for preparing for these exams]
        Top Institutions in India for Postgraduate Studies:
        [Institution Name 1]: [Brief description, website link, indicative fee structure]
        [Institution Name 2]: [Brief description, website link, indicative fee structure]
        Top Institutions Abroad for Postgraduate Studies:
        [Institution Name 1]: [Brief description, website link, indicative fee structure]
        [Institution Name 2]: [Brief description, website link, indicative fee structure]
        Skill Development and Networking:
        Internships: [Importance and tips on finding internships]
        Skill Enhancement: [Additional skills, courses, certifications, and workshops]
        Networking: [Importance and tips on connecting with professionals]
        Entry into Work Life:
        Entry-Level Jobs: [Types of entry-level jobs and brief descriptions]
        Salaries in India: [Indicative entry-level salary range in India]
        Career Progression Tips: [Skills to develop, certifications to pursue, strategies for advancement]
        Companies Offering Relevant Roles: [List of companies with brief descriptions]
        Congratulations and Best Wishes:
        Congratulatory Note: Congratulations on taking this important step towards planning your career!
        Best Wishes: Wishing you all the best for a successful and fulfilling career in %s!

        """ % (qualification, careerTitle,qualification, careerTitle,careerTitle)
        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=step8question)], )
        careerSteps8 = chat.choices[0].message.content
        # print(f"ChatGPT Reply for step 8 for {careerTitle}-: {career_steps8}")
        update_step(careerTitle, qualification, 'step_8', careerSteps8)
        update_career_status(careerTitle, 'Completed')
        log.debug('insert career steps for user=%s', userId)

        responseData['message'] = "Career searched"
        responseData['status_code'] = 200
        return responseData
    except Exception as error:
        log.error('Error in search career steps for user id=%s', userId, exc_info=True)
        update_career_status(careerTitle, 'Failed')
        raise error


async def chat_answer(data):
    try:
        userId = data['userId']
        question = data['question']
        log = get_gpt_logger()
        log.debug('Getting answer for userId =%s, question=%s', userId, question)
        responseData = {}
        projectFolder = os.path.expanduser('../..')
        load_dotenv(os.path.join(projectFolder, '.env'))
        mistralAPIKey = os.getenv('MISTRAL_API_KEY')
        mistralModel = os.getenv('MISTRAL_AI_MODEL')
        client = MistralAsyncClient(api_key=mistralAPIKey)

        chat = await client.chat(model=mistralModel, messages=[ChatMessage(role="user", content=question)],
                                 )
        chatAnswer = chat.choices[0].message.content
        log.debug('Received chat answer for userId=%s, answer=%s', userId, chatAnswer)
        tokenUsed = chat.usage.total_tokens
        update_token_usage(userId, tokenUsed)

        responseData['answer'] = chatAnswer
        responseData['status_code'] = 200
        return responseData
    except Exception as error:
        log.debug('Error in getting answer for userId =%s, question=%s', userId, question, exc_info=True)
        raise error
