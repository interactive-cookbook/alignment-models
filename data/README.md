##Data Format

There is one folder per dish containing a file with gold alignments (crowdsourced) called ```alignments.tv``` and a sub-directory ```/recipes``` containing the individual recipe files.

#Recipe Files
Recipe files describe *action graphs* in CoNLL-U format, i.e. action tokens are tagged with ```B-A``` or ```I-A``` (IOB2 tagging scheme), all other tokens are not tagged (i.e. ```O``` tag). The ```HEAD, REL``` and ```DEPS``` columns of ```B-A```-tagged tokens specify the relations between the respective action and its parent nodes. <!-- The alignment model does take the DEPS column into account, doesn't it? I.e. it is able to read in multiple parent nodes for one action? -->

#Alignemtn Files
One alignment file specifies the (gold standard) alignments between all recipes in the ```/recipes``` directory. In each line, the first element is the recipe name of the left recipe (i.e. source recipe), the second element is a token ID of the first token of an action in said left recipe. The right recipe (i.e. target recipe) is specified in the third column and the fourth and final element in each line is the token id of the first token of the target action.
