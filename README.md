# CekManis

  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#project-overview">Project Overview</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#running">Running</a></li>
      </ul>
    </li>
    <li><a href="#feature">Feature</a></li>
    <li><a href="#demo">demo</a></li>
    <li><a href="#contributors">Contributors</a></li>
    <li><a href="#disclaimer">Disclaimer </a></li>
  </ol>


## Project Overview

CekManis is a Generative AI prototype designed as a public health tool to address  Malaysia's alarming rates of obesity and diabetes which are the highest in ASEAN. The project aligns directly with the Health Ministry's mandatory Nutri-Grade Malaysia 
labelling system and the national __'WAR ON SUGAR’__ campaign.

---
## Getting Started
> [!NOTE]  
> We highly recommended to develop the project using Python 3.13.0 or later in the Visual Studio Code (VS Code).

### Installation
1.
```
git clone https://github.com/tanpeishing123/hackathon2025.git
```
2. Create a virtual environment in VS code:  
```
py -m venv venv
```
3. Install the requirement.txt:
```
pip install -r requirements.txt
```

4. Download the `proj_9a8190b20789a318daf028ae.parquet` from [JamAI](JamAI/proj_9a8190b20789a318daf028ae.parquet) file  
5. Import the project and get the Project ID and JamAI API Key from [JamAI Base](https://www.jamaibase.com/)  
6. In VS Code, rename the file `secrets.toml.example` to `secrets.toml` in`.streamlit`.
7. Enter your project ID and JamAI API Key inside `secrets.toml`  

---
### Running
8.
```
streamlit run "Home.py"
```
---
## Feature
- Manual Input
- Scan Nutrition Fact
- Scan the Fresh Prepared Drinks
- Scan the Beverage Menu
- Chatbot  
English and Bahasa Melayu are supported.
---
## Demo
---
## Contributors
We extend our sincere gratitude to everyone who contributed to this project, making it better, more stable, and more feature-rich. Your time and effort are deeply appreciated!
A massive thank you to the following individuals for their exceptional work and dedication:

- Choong Zhuo Lin 
- Goh Zhi Xuan 
- Tan Pei Shing
- Yee Wing Yong
- Lee Kai Hong
---
## Disclaimer  
> [!Important]
> The data and predictions provided by CekManis are generated for **educational** and **awareness** purposes only. 
