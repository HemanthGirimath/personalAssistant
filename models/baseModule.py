from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import different model providers
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.credentials import openai_api_key, gemini_api_key

class ModelSelector:
    def __init__(self):
        """Initialize with available models"""
        self.available_models = {}
        
        # Initialize OpenAI models if API key is available
        if openai_api_key:
            try:
                self.available_models["gpt-4"] = self._get_openai_model("gpt-4")
                self.available_models["gpt-3.5-turbo"] = self._get_openai_model("gpt-3.5-turbo")
                print("OpenAI models initialized successfully")

            except Exception as e:
                print(f"Failed to initialize OpenAI models: {e}")
            try:
                self.available_models["models/gemini-2.5-pro-exp-03-25"] = self._get_gemini_model("models/gemini-2.5-pro-exp-03-25")
                self.available_models["gemini-2.0-flash"] = self._get_gemini_model("gemini-2.0-flash")
                print("Gemini models initialized successfully")

            except Exception as e:
                print("failed to initialize Gemini models: {e}")

        # Set default model to first available one
        if self.available_models:
            self.current_model_name = next(iter(self.available_models))
            self.current_model = self.available_models[self.current_model_name]
        else:
            print("Warning: No models were successfully initialized")
            self.current_model_name = None
            self.current_model = None

    def _get_openai_model(self, model_name):
        """Create OpenAI model instance"""
        return ChatOpenAI(
            model=model_name, 
            temperature=0.7,
            openai_api_key=openai_api_key
        )
    
    def _get_gemini_model(self, model_name):
        """Create Google Gemini model instance"""
        return ChatGoogleGenerativeAI(
            model=model_name, 
            temperature=0.7,
            google_api_key=gemini_api_key
        )
    
    def list_available_models(self):
        """Return list of available models"""
        return list(self.available_models.keys())
    
    def set_model(self, model_name:str):
        """Set current model to use"""
        if model_name in self.available_models:
            self.current_model_name = model_name
            self.current_model = self.available_models[model_name]
            return self.current_model
        else:
            return f"Model {model_name} not found. Available models: {', '.join(self.list_available_models())}"
    
    def get_current_model(self):
        """Return current model name"""
        return self.current_model_name
    
    def add_custom_model(self, model_name, model_instance):
        """Add a custom model"""
        if not isinstance(model_instance, BaseChatModel):
            return "Error: model must be a LangChain chat model"
        
        self.available_models[model_name] = model_instance
        return f"Added model {model_name}"
    
    def query(self, prompt):
        """Run a query using the current model"""
        try:
            # Create a simple chain
            chain = self.current_model | StrOutputParser()
            return chain.invoke(prompt)
        except Exception as e:
            return f"Error with {self.current_model_name}: {str(e)}"

    def structured_query(self, template, **kwargs):
        """Run a structured query with a template"""
        try:
            print(f"Template: {template}")
            print(f"kwargs: {kwargs}")
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | self.current_model | StrOutputParser()
            print("model response :{result}")
            return chain.invoke(kwargs)
    
        except Exception as e:
            print(f"Error with {self.current_model_name}: {str(e)}")
            return f"Error with {self.current_model_name}: {str(e)}"

