<img width="1511" alt="YPopUpBanner" src="https://github.com/NeilSachdeva/YPopUp/assets/60718463/dc9eb077-fa2a-4e94-9944-3bb672f2b0af">

# YPopUp
This repository contains the algorithm we use for the Y Pop-Up Lottery and subsequent seat selection.

Put simply, The neil-draw algorithm takes in Y Pop-Up Lottery submission data and picks a set of lucky customers to attend that week's Y Pop-Up opening!
The algorithm takes 2 key factors into account:
### 1. The number of times a person has tried to reserve a table and not gotten one
### 2. The most recent reservation a person has had

Our algorithm positively weights factor 1, meaning the more times you apply, the higher your chance of getting a table. This chance increases exponentially.
Conversely, our algorithm negatively weights factor 2, meaning if you have very recently attended a Y Pop-Up opening, you have a smaller chance of getting a table. An important note is that this negative weighting very quickly fades, and your factor 1 count continues to increase, so we encourage people to continue applying!

After getting our list of lucky folks, our algorithm then assigns tables and time slots based on our customer's requested specifications. The data_formatting.py script helps take care of some pre-processing required to merge various data sources together.

Hopefully, this provides some clarity as to how we operate the lottery. See you at the next opening!
