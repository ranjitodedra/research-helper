# Algorithm Page Prompt

I'm writing an academic journal paper in computer science/data science/ai/ml. 
I need help creating algorithm explaination just like attached image.

the full python code of algorithm is also attached. now in my research paper we are suppose to add this king of pahe where we explain the code in like pseudo code. this is heuristic code.

Goal:
- I want to understand what exactly I need to add on this page and what I dont need to add withoug missing anything important or adding somthing extra.
- take look at code and image file and make point wise list that helps to create latex code of that image attached for any algorithm.

# The Rewrite Prompt


I need help improving the following text while maintaining academic rigor and clarity.

Original text:
[Paste your text here]

Please provide:
Alternative word choices - Suggest more precise, formal, or varied vocabulary where appropriate. Highlight any informal language, redundancies, or weak verbs that could be strengthened.

Style improvements - Identify areas where:
Sentence structure could be more concise or clear

Passive voice should be changed to active (or vice versa, where appropriate)
Transitions between ideas could be smoother
Technical terminology could be more precise


Paraphrasing options - Offer 2-3 alternative ways to express key sentences or complex ideas, especially those that seem unclear or overly wordy.
Clarity for readers - Point out any jargon or concepts that may need additional explanation for a broader academic audience.

Context:
I'm writing an academic journal paper in computer science/data science/ai/ml. 
Target journal: IEEE
Intended audience: experts in computer science field, interdisciplinary researchers
Specific concerns: [e.g., 'This paragraph feels repetitive' or 'I'm unsure if this argument is clear']

Please maintain the academic tone and ensure all suggestions preserve the original meaning and argument.







# Editing

• Mass of rolling inertia: 
• Rolling resistance coefficient: 
• Air density: 
• Vehicle cross-sectional area: 
• Drag coefficient: Cx = 
• Average road angle: 
• EV battery capacity: 
• acceleration:
• Battery threshold: 


# Latex code for images and CSV file

Input:
- a folder called images.
- each folder in images contain images(plots like barcharts, linecharts etc) and csv data files.
- csv and png file with same name represents that that CSV file is used as dataframe to create that graph.

Contenxt:
- I will upload this folder images to my Overleaf. In Overleaf I have a tex file. In that tex I want to add images so provide me latex code to first write /subsection{nameoffolder} so subsection should be name of folder and after that image should be added and after that add explaination of that graph.

for generating the explaination of each graph use the image and CSV data file. a image and csv file pointing same graph have same name. For what exactly to produce look at the following Produce a clear analytic report text with the following sections. Note that following sections should be used to just generate the content for writing contenct I want in pragraph style writing following content in 2-3 pragraphs per graph. Keep language formal and concise. I'm writing an academic journal paper in computer science/data science/ai/ml. Target journal: IEEE
Intended audience: experts in computer science field, interdisciplinary researchers
Specific concerns: [e.g., 'This paragraph feels repetitive' or 'I'm unsure if this argument is clear'] Please maintain the academic tone and ensure all suggestions preserve the original meaning and argument.

Sections for explaination generation idea:

1) Title / Chart type
- One-line: chart type and short title inferred from figure.

2) Axes & legend
- X-axis: label and unit (or "label unreadable")
- Y-axis: label and unit (or "label unreadable")
- Legend / Series: list series names (or "legend unreadable")

3) Key quantitative findings (bullet list)
- Up to 3 bullets giving measurable facts (e.g., "Series A increases from ~X to ~Y", or "peak at X"). If values are not legible, write "exact values not readable — describe trend only."

4) Trends & comparison (2–3 sentences)
- Describe overall trend(s), relative differences, crossovers.

5) Anomalies & possible explanations (1–2 bullets)
- Note sudden jumps, dips, outliers and plausible causes.

6) Limitations & confidence
- Which parts of the figure were unreadable or ambiguous and how that affects confidence (low/medium/high).

7) Recommended next steps (2 bullets)
- e.g., compute percent change, add error bars, provide raw data table, run statistical test.

Output as plain text without clearly labeled sections,and for all subplots, repeat subsection, images, analysis for each subplot and provide full Latex code that I can paste in existing latex code and note that I will just update the image folder note it for paths.

Output: a Latex File
- /subsection{name of the folder}
- for each graph image and csv data in that folder
    - Image (starting with (a) then (b) ... so on)
    - description - is paragraph style text that describes the graph from CSV file 


# from ipynb file to exract CSV files and images of Graph

Write a Python script that:
- Scans a given directory for .ipynb files.
- Parses each notebook (use nbformat) without executing it.
- For every top-level markdown # Title create a folder ./images/<Title>/ (slugify/sanitize names).

Inside each # Title section, for every ## Subtitle:
- Find the first dataframe output in that subtitle block and save it as Subtitle.csv in the parent Title folder (use pandas to read HTML/text outputs when needed).
- Find the first image/plot output that follows and save it as Subtitle.png in the same folder (support inline PNG outputs).
- If either output is missing, skip that file but continue processing.
- Use safe filenames, handle duplicates (e.g., add suffix), and create folders as needed.
- Print a concise log of files saved and notebooks processed.
- Use only standard libs plus nbformat and pandas. Keep the code robust and commented.

# brain storm

- the main poit of comaparison between heuristic and cplex is that cplex is better performance wise as the size or program increases the runtime becomes not feasiable. 

- main poit of comparing heuristic with other programs they perform better for smalle examples but for large example my herusitc seems to do well compare with others. 

- heuristic can go to massive examples


# check

Total Travel Time: 409.28 minutes
Total Energy Consumed: 58.157 kWh
Total Distance Covered: 325.74 km

# Hate me


Change the way of introducing several methods. This is not the right way.
"
Exact methods also solve EVRP subproblems:
"




# Combine 

I'm writing an academic journal paper in computer science/data science/ai/ml.

now in current paper is on routing decision with EV charging station and Electric road system, right now i am writing second parapraph of introduction section, in first I talked about general thing like how emision can be reduved by EV and how there are problems with EV and how electric road is this new thig that could help use. now I want you to write next paragrah, where i talk about electric road system. now I am added sentence with reference from other paper by my self so I want you to write in way that i dont need to refere to any paper(no hard numbers or facts). also not that I dont need to show it as ulimate solution as my paper will consider it with charging staions, so whil keeping all this in ming write parapragh for me.




Using the provided research papers as sources, synthesize one cohesive academic paragraph introducing dynamic wireless charging (also known as electric road systems).

The paragraph should:

- explain disadvantages of ERS
- why charging station can co exist with electric roads and they are not going to replace charging station.

Do not copy text verbatim from the sources. Paraphrase and integrate ideas naturally.

After the paragraph, provide a source traceability note mapping each major claim to:

the corresponding paper,

page or section number (if available), and

2–4 distinctive keywords or phrases that can be searched to locate the original passage.

Context: This paragraph frames dynamic wireless charging as a complementary alternative to stationary charging infrastructure, not a replacement.

Audience: experts in computer science and interdisciplinary EV systems researchers.
Tone: formal, concise, IEEE-style.

Only cite ideas that are original contributions or direct analyses of the attached paper.
Do not cite statements that the paper attributes to other works (e.g., “as shown in [12]”).
If a claim originates from another paper, mark it as “secondary reference” and do not use it unless explicitly permitted.

I'm writing an academic journal paper in computer science/data science/ai/ml. 
I need help improving the following text while maintaining academic rigor and clarity.

Original text:
In contrast to previous studies, this work integrates three key capabilities—on-the-fly rerouting, dynamic charging-mode selection between electrified road segments and conventional charging stations, and load-aware energy consumption modeling—within a unified optimization framework. To address the computational complexity of the problem, we employ two complementary methodologies: a Mixed-Integer Linear Programming (MILP) formulation to establish an optimal baseline solution, and a genetic algorithm to obtain high-quality near-optimal solutions with improved scalability under dynamic traffic and energy conditions. Together, these approaches enable adaptive routing and efficient energy management for electric delivery vehicles operating in dense urban environments.

Please provide:
Alternative word choices - Suggest more precise, formal, or varied vocabulary where appropriate. Highlight any informal language, redundancies, or weak verbs that could be strengthened.

Style improvements - Identify areas where:
Sentence structure could be more concise or clear

Passive voice should be changed to active (or vice versa, where appropriate)
Transitions between ideas could be smoother
Technical terminology could be more precise

Paraphrasing options - Offer 2-3 alternative ways to express key sentences or complex ideas, especially those that seem unclear or overly wordy.
Clarity for readers - Point out any jargon or concepts that may need additional explanation for a broader academic audience.

Context:

Target journal: IEEE
Intended audience: experts in computer science field, interdisciplinary researchers
Specific concerns: [e.g., 'This paragraph feels repetitive' or 'I'm unsure if this argument is clear']

Please maintain the academic tone and ensure all suggestions preserve the original meaning and argument.

1. Questions you must answer about your project

Answer these in plain English. Bullet points are fine.

A. Context & motivation

What broader field does your thesis belong to?

Why is this problem important now (technological, societal, practical reason)?

B. Problem definition

What exact problem are you solving?

What makes this problem hard or unsolved in existing work?

C. Objectives

What are the main objectives of your thesis?
(e.g., minimize X, optimize Y, handle Z)

D. Methodology (exact)

What exact model or formulation do you use first?

What assumptions or constraints are central to your model?

E. Methodology (scalable / practical)

Why does the exact method not scale?

What approximate / heuristic / algorithmic methods do you propose?

What does each method primarily optimize?

F. Novelty

What does your work do simultaneously that prior work treats separately?

What is the key conceptual contribution (not implementation detail)?

G. Impact

What practical or theoretical insight does your work provide?

How can this be used or extended in the future?

















======================================================================================================================================================

