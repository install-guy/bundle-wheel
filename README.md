\# HR Bundle Campaign Engine



This repo powers the creation of structured marketing content for Hobby Etc and Hot Racing upgrade bundles.



The goal is to turn product bundles into a repeatable content system:

\- Bundle → Influencer Content → Landing Page → Blog → Internal Links → Conversion → Retention



\---



\## 🚀 What this does



Given a bundle JSON file, this system will generate:



\- Landing page content

\- Blog post content

\- Meta title + description

\- Internal linking structure



All outputs are saved into `/output/<bundle-slug>/`



\---



\## 📁 Project Structure



/data  

Structured inputs (bundles, products, SEO rules)



/templates  

Reusable content templates (landing pages, blogs, email, etc)



/scripts  

Runnable scripts to generate content



/src  

Core logic (generators, validators, renderers)



/output  

Generated content ready for review or publishing



/docs  

Strategy, prompts, and workflows



\---



\## 🧠 How it works



1\. Create a bundle JSON file in:

&#x20;  `/data/bundles/`



2\. Run the generator script:

