
"""
Usage: python main.py model_name embedding_name

(model_name: ['Sequence' : Sequential ordering of alignments, 
              'Cosine_similarity' : Cosine model, 
              'Naive' : Common Action Pair Heuristics model,
              'Alignment-no-feature' : Base Alignment model, 
              'Alignment-with-feature' : Extended Alignment model])

(embedding_name : ['bert' : BERT embeddings,
                   'elmo' : ELMO embeddings])
"""

# importing libraries

import torch
import os
import flair
import argparse
import torch.nn as nn
import torch.optim as optim
import pandas as pd

from model import AlignmentModel
from cosine_similarity_model import SimpleModel
from sequence_model import SequenceModel
from naive_model import NaiveModel
from transformers import BertTokenizer, BertModel
from flair.data import Sentence
from flair.embeddings import ELMoEmbeddings
from constants import OUTPUT_DIM, LR, EPOCHS, FOLDS, HIDDEN_DIM1, HIDDEN_DIM2, CUDA_DEVICE

from datetime import datetime
from constants import (
    folder,
    alignment_file,
    recipe_folder_name,
    destination_folder1,
    destination_folder2,
    destination_folder3,
    destination_folder4,
)
from utils import (
    fetch_recipe_train,
    fetch_dish_train,
    save_metrics,
    save_checkpoint,
    load_checkpoint,
    save_predictions,
    create_acc_loss_graph,
    save_vocabulary,
    load_vocabulary
)


# from script main.py
# no more function, merged ith train-related functions

device = torch.device(CUDA_DEVICE if torch.cuda.is_available() else "cpu")
flair.device = device
    
parser = argparse.ArgumentParser(description = """Automatic Alignment model""")
parser.add_argument('model_name', type=str, help="""Model Name; one of {'Simple', 'Naive', 'Alignment-no-feature', 'Alignment-with-feature'}""") # TODO: add options for fat graphs (with parents and grandparents)
parser.add_argument('--embedding_name', type=str, default='bert', help='Embedding Name (Default is bert, alternative: elmo)')
parser.add_argument('--cuda-device', type=str, help="""Select cuda; default: cuda:0""")
args = parser.parse_args()

model_name = args.model_name
    
embedding_name = args.embedding_name

if args.cuda_device:
    device = torch.device("cuda:"+args.cuda_device if torch.cuda.is_available() else "cpu")
    flair.device = device 

print("-------Loading Model-------")

# Loading Model definition
    
if embedding_name == 'bert' :

    tokenizer = BertTokenizer.from_pretrained(
        "bert-base-uncased"
    )  # Bert Tokenizer
    
    emb_model = BertModel.from_pretrained("bert-base-uncased", output_hidden_states=True).to(
        device
    )  # Bert Model for Embeddings
        
    embedding_dim = emb_model.config.to_dict()[
        "hidden_size"
    ]  # BERT embedding dimension
    
    # print(bert)
    
elif embedding_name == 'elmo' :
        
    tokenizer = Sentence #Flair sentence for ELMo embeddings
       
    emb_model = ELMoEmbeddings('small')
        
    embedding_dim = emb_model.embedding_length

# -----------------------------------------------------------------------


# copying and adapting from trainig_testing.py
# test-related functions in --> test.py

# Training Process Class
class Folds_Train:
    def run_model(
        self,
        dish_dict,
        dish_group_alignments,
        emb_model,
        tokenizer,
        model,
        device,
        embedding_name,
        criterion=None,
        optimizer=None,
        total_loss=0.0,
        step=0,
        correct_predictions=0,
        num_actions=0,
        mode="Training",
        model_name="Alignment Model",
    ):
        """
        Function to run the Model

        Parameters
        ----------
        dish_dict : dict
            Contains all information for one dish. Keys: recipe names. Values: dictionaries with keys "Embedding_Vectors", "Vector_Lookup_Lists", "Action_Dicts_List" and values according to fetch_recipe().
        dish_group_alignments : pd.DataFrame
            All alignments (token ID's) for one dish, grouped by pairs of recipe names.
        emb_model : Embedding Model object
            Model.
        tokenizer : Tokenizer object
            Tokenizer.
        model : AlignmentModel object
            Alignment model.
        device : object
            torch device where model tensors are saved.
        criterion : Cross Entropy Loss Function, optional
            Loss Function. The default is None.
        optimizer : Adam optimizer object, optional
            Optimizer. The default is None.
        total_loss : Float, optional
            Total Loss after Training/Validation. The default is 0.0.
        step : Int, optional
            Each Training/Validation step. The default is 0.
        correct_predictions : Int, optional
            Correction predictions for a Dish. Defaults is 0.
        num_actions : Int, optional
            Number of actions in a Dish. Defaults is 0.
        mode : String, optional
            Mode of Process - ("Training", "Validation", "Testing"). The default is "Training".
        model_name : String, optional
            Model name - ("Alignment Model", "Simple Model"). Default is "Alignment Model".


        """

        """
        data_folder = os.path.join(folder, dish)  # dish folder
        recipe_folder = os.path.join(data_folder, recipe_folder_name)  # recipe folder, e.g. data/dish-name/recipes
        

        alignment_file_path = os.path.join(
            data_folder, alignment_file
        )  # alignment file, e.g. data/dish-name/alignments.tsv

        # Gold Standard Alignments between all recipes for dish
        alignments = pd.read_csv(
            alignment_file_path, sep="\t", header=0, skiprows=0, encoding="utf-8"
        )
        

        # Group by Recipe pairs
        dish_group_alignments = alignments.groupby(["file1", "file2"])

        if mode == "Testing":
            results_df = pd.DataFrame(
                columns=["Action1_id", "True_Label", "Predicted_Label"]
            )

        for key in dish_group_alignments.groups.keys():

            recipe1_filename = os.path.join(recipe_folder, key[0] + ".conllu")
            recipe2_filename = os.path.join(recipe_folder, key[1] + ".conllu")



            embedding_vector1, vector_lookup_list1, recipe_dict1 = fetch_recipe(
                recipe1_filename, emb_model, tokenizer, device, embedding_name,
            )
            embedding_vector2, vector_lookup_list2, recipe_dict2 = fetch_recipe(
                recipe2_filename, emb_model, tokenizer, device, embedding_name,
            )
        """
        
        if mode == "Testing":
            results_df = pd.DataFrame(
                columns=["Action1_id", "True_Label", "Predicted_Label"]
            )

        for key in dish_group_alignments.groups.keys():
            
            recipe1 = dish_dict[key[0]] 
            recipe2 = dish_dict[key[1]] 

            recipe_pair_alignment = dish_group_alignments.get_group(key)

            #for node in action_dicts_list1[1:]:
            for node in recipe1["Action_Dicts_List"][1:]:

                if mode == "Training":
                    optimizer.zero_grad()

                # True Action Id
                action_line = recipe_pair_alignment.loc[
                    recipe_pair_alignment["token1"] == node["Action_id"]
                ]

                if not action_line.empty:

                    true_label = action_line["token2"].item()

                    # True Action Id index
                    labels = [
                        i
                        for i, node in enumerate(recipe2["Action_Dicts_List"])
                        if node["Action_id"] == true_label
                    ]
                    labels_tensor = torch.LongTensor([labels[0]]).to(device)

                    action1 = node["Action"]
                    parent_list1 = node["Parent_List"]
                    child_list1 = node["Child_List"]

                    # Generate predictions using our Alignment Model

                    if model_name == "Alignment Model":
                        prediction = model(
                            action1.to(device),
                            parent_list1,
                            child_list1,
                            recipe1["Embedding_Vectors"],
                            recipe1["Vector_Lookup_Lists"],
                            recipe2["Action_Dicts_List"],
                            recipe2["Embedding_Vectors"],
                            recipe2["Vector_Lookup_Lists"],
                        )

                    elif model_name == "Simple Model":
                        prediction = model(
                            action1.to(device),
                            recipe1["Embedding_Vectors"],
                            recipe1["Vector_Lookup_Lists"],
                            recipe2["Action_Dicts_List"],
                            recipe2["Embedding_Vectors"],
                            recipe2["Vector_Lookup_Lists"],
                        )

                    # print(prediction)

                    num_actions += 1

                    # Predicted Action Id
                    pred_label = recipe2["Action_Dicts_List"][torch.argmax(prediction).item()][
                        "Action_id"
                    ]

                    if true_label == pred_label:
                        correct_predictions += 1

                    if mode == "Training" or mode == "Validation":
                        loss = criterion(prediction, labels_tensor)  # Loss

                        if mode == "Training" and not true_label == pred_label:
                            loss.backward()
                            optimizer.step()

                        total_loss += loss.item()
                        step += 1

                    elif mode == "Testing":

                        results_dict = {
                            "Action1_id": node["Action_id"],
                            "True_Label": true_label,
                            "Predicted_Label": pred_label,
                        }

                        # Store the prediction
                        results_df = results_df.append(results_dict, ignore_index=True)

        if mode == "Training" or mode == "Validation":

            return correct_predictions, num_actions, total_loss, step

        elif mode == "Testing":

            return correct_predictions, num_actions, results_df

        return None

    #####################################

    def train(
        self, dish_list, embedding_name, emb_model, tokenizer, model, criterion, optimizer, device
    ):
        """
        Train Function

        Parameters
        ----------
        dish_list : List
            List of dish names.
        emb_model : Embedding Model object
            Model.
        tokenizer : Tokenizer object
            Tokenizer.
        model : AlignmentModel object
            Alignment model.
        criterion : Cross Entropy Loss Function
            Loss Function.
        optimizer : Adam optimizer object
            Optimizer.
        device : object
            torch device where model tensors are saved.

        """

        train_loss = 0.0
        step = 0
        correct_predictions = 0
        num_actions = 0

        model.train()

        mode = "Training"
        
        for dish in dish_list:

            correct_predictions, num_actions, train_loss, step = self.run_model(
                self.dish_dicts[dish], 
                self.gold_alignments[dish], 
                embedding_name = embedding_name,
                emb_model=emb_model,
                tokenizer=tokenizer,
                model=model,
                device=device,
                criterion=criterion,
                optimizer=optimizer,
                total_loss=train_loss,
                step=step,
                correct_predictions=correct_predictions,
                num_actions=num_actions,
                mode=mode,
            )

        average_train_loss = train_loss / (step - 1)
        average_train_accuracy = correct_predictions * 100 / num_actions

        return average_train_loss, average_train_accuracy

    #####################################

    def valid(self, dish, embedding_name, emb_model, tokenizer, model, criterion, device):
        """
        Valid Function

        Parameters
        ----------
        dish : String
            Dish name.
        emb_model : Embedding Model object
            Model.
        tokenizer : Tokenizer object
            Tokenizer.
        model : AlignmentModel object
            Alignment model.
        criterion : Cross Entropy Loss Function
            Loss Function.
        device : object
            torch device where model tensors are saved.


        """

        valid_loss = 0.0
        step = 0
        correct_predictions = 0
        num_actions = 0

        model.eval()

        mode = "Validation"

        with torch.no_grad():

            correct_predictions, num_actions, valid_loss, step = self.run_model(
                self.dish_dicts[dish], 
                self.gold_alignments[dish], 
                embedding_name = embedding_name,
                emb_model=emb_model,
                tokenizer=tokenizer,
                model=model,
                device=device,
                criterion=criterion,
                total_loss=valid_loss,
                step=step,
                correct_predictions=correct_predictions,
                num_actions=num_actions,
                mode=mode,
            )

        average_valid_loss = valid_loss / step
        average_valid_accuracy = correct_predictions * 100 / num_actions

        return average_valid_loss, average_valid_accuracy

    #####################################

    def training_process(
        self,
        dish_list,
        embedding_name,
        emb_model,
        tokenizer,
        model,
        optimizer,
        criterion,
        num_epochs,
        saved_file_path,
        saved_metric_path,
        saved_graph_path,
        device,
    ):
        """
        Training Process function

        Parameters
        ----------
        dish_list : List
            List of all recipes in training set
        emb_model : Embedding Model object
            Model.
        tokenizer : Tokenizer object
            Tokenizer.
        model : AlignmentModel object
            Alignment model.
        optimizer : Adam optimizer object
            Optimizer.
        criterion : Cross Entropy Loss Function
            Loss Function.
        num_epochs : Int
            Number of Epochs.
        saved_file_path : String
            Trainied Model path.
        saved_metric_path : Sring
            Training Metrics file path.
        saved_graph_path : String
            Training/Validation accuracy and loss graph path.
        device : object
            torch device where model tensors are saved.


        """

        # initialize running values
        train_loss_list = []  # List of Training loss for every epoch
        valid_loss_list = []  # List of Validation loss for every epoch
        epoch_list = []  # List of Epochs
        train_accuracy_list = []
        valid_accuracy_list = []

        best_valid_accuracy = best_train_accuracy = float(
            "-Inf"
        )  # Stores the best Validation/Training Accuracy
        best_valid_loss = best_train_loss = float(
            "Inf"
        )  # Stores the best Validation/Training Loss

        valid_dish_id = len(dish_list) - 1  # Validation dish index
        train_dish_list = dish_list.copy()
        valid_dish = train_dish_list.pop(valid_dish_id)

        # Training loop

        for epoch in range(num_epochs):

            # Calculate average training loss per epoch
            average_train_loss, average_train_accuracy = self.train(
                train_dish_list,
                embedding_name,
                emb_model,
                tokenizer,
                model,
                criterion,
                optimizer,
                device,
            )

            # calculate average validation loss per epoch
            average_valid_loss, average_valid_accuracy = self.valid(
                valid_dish, embedding_name, emb_model, tokenizer, model, criterion, device
            )

            train_loss_list.append(average_train_loss)
            valid_loss_list.append(average_valid_loss)
            train_accuracy_list.append(average_train_accuracy)
            valid_accuracy_list.append(average_valid_accuracy)
            epoch_list.append(epoch)

            # print progress
            print(
                "Epoch [{}/{}], Train Loss: {:.4f}, Train Accuracy: {:.4f}, Valid Loss: {:.4f}, Valid Accuracy: {:.4f}".format(
                    epoch + 1,
                    num_epochs,
                    average_train_loss,
                    average_train_accuracy,
                    average_valid_loss,
                    average_valid_accuracy,
                )
            )

            # saving checkpoint
            if best_valid_accuracy < average_valid_accuracy:
                best_valid_accuracy = average_valid_accuracy
                best_train_accuracy = average_train_accuracy
                best_valid_loss = average_valid_loss
                best_train_loss = average_train_loss
                save_checkpoint(
                    saved_file_path,
                    model,
                    optimizer,
                    best_valid_loss,
                    best_valid_accuracy,
                )
                save_metrics(
                    saved_metric_path,
                    train_loss_list,
                    valid_loss_list,
                    train_accuracy_list,
                    valid_accuracy_list,
                    epoch_list,
                )

        # create_acc_loss_graph(epoch_list, train_loss_list, valid_loss_list)

        save_metrics(
            saved_metric_path,
            train_loss_list,
            valid_loss_list,
            train_accuracy_list,
            valid_accuracy_list,
            epoch_list,
        )

        print("Finished Training!")

        create_acc_loss_graph(saved_metric_path, device, saved_graph_path)

        return (
            best_train_accuracy,
            best_valid_accuracy,
            best_train_loss,
            best_valid_loss,
        )

    #####################################

    def run_folds_train(
        self,
        embedding_name,
        emb_model,
        tokenizer,
        model,
        optimizer,
        criterion,
        num_epochs,
        num_folds,
        device,
        with_feature=True,
    ):
        """
        Running 10 fold cross validation for alignment models

        Parameters
        ----------
        embedding_name : String
            Either 'elmo' or 'bert'.
        emb_model : Embedding Model object
            Model.
        tokenizer : Tokenizer object
            Tokenizer.
        model : AlignmentModel object
            Alignment model.
        optimizer : Adam optimizer object
        num_epochs : Int
            Number of Epochs.
        num_folds : Int
            Number of Folds.
        device : object
            torch device where model tensors are saved.
        with_feature : boolean; Optional
            Check whether to add features or not. Default value True.

        """

        print("-------Loading Data-------")

        dish_list = os.listdir(folder)

        dish_list = [dish for dish in dish_list if not dish.startswith(".")]
        dish_list.sort() 
        self.dish_dicts = dict()
        self.gold_alignments = dict()

        for dish in dish_list:
        
            dish_dict, dish_group_alignments = fetch_dish_train(dish, folder, alignment_file, recipe_folder_name, emb_model, tokenizer, device, embedding_name)
        
            self.dish_dicts[dish] = dish_dict
        
            self.gold_alignments[dish] = dish_group_alignments

        print("Data successfully loaded for dishes ", dish_list)

        fold_result_df = pd.DataFrame(
            columns=[
                "Fold",
                "Train_Loss",
                "Train_Accuracy",
                "Valid_Loss",
                "Valid_Accuracy",
                "Fold_Timelapse_Minutes"
            ]
        )  # , "Test_Dish1_accuracy", "Test_Dish2_accuracy"])

        #test_dish_id = len(dish_list) - 1 # TODO: why though? Why not iterate over dish_list 5 lines later or use `test_dish_id = fold`?

        if with_feature:
            destination_folder = destination_folder1

        else:
            destination_folder = destination_folder2

        print("-------Cross Validation Folds-------")

        for fold in range(num_folds):

            start = datetime.now()

            saved_file_path = os.path.join(
                destination_folder, "model" + str(fold + 1) + ".pt"
            )  # Model saved path
            saved_metric_path = os.path.join(
                destination_folder, "metric" + str(fold + 1) + ".pt"
            )  # Metric saved path
            saved_graph_path = os.path.join(destination_folder, "loss_acc_graph" + str(fold + 1) + ".png")

            train_dish_list = dish_list.copy()
            #test_dish_list = [
            #    train_dish_list.pop(test_dish_id)
            #]  # train_dish_list contains 9 dish names, test_dish_list contains 1 dish name

            #test_dish_id -= 1

            #if test_dish_id == -1:

            #    test_dish_id = len(dish_list) - 1 # TODO: why? shouldn't it be 0, if anything? or maybe just move the line ```test_dish_id -= 1``` to the end of the loop?

            print("Fold [{}/{}]".format(fold + 1, num_folds))

            print("-------Training-------")

            (
                train_accuracy,
                valid_accuracy,
                train_loss,
                valid_loss,
            ) = self.training_process(
                train_dish_list,
                embedding_name,
                emb_model,
                tokenizer,
                model,
                optimizer,
                criterion,
                num_epochs,
                saved_file_path,
                saved_metric_path,
                saved_graph_path,
                device,
            )

            #print("-------Testing-------")

            #(
            #    test_accuracy_list,
            #    test_accuracy,
            #    total_correct_predictions,
            #    total_actions,
            #) = self.testing_process(
            #    test_dish_list,
            #    embedding_name,
            #    emb_model,
            #    tokenizer,
            #    model,
            #    optimizer,
            #    saved_file_path,
            #    saved_metric_path,
            #    destination_folder,
            #    device,
            #)

            end = datetime.now()

            elapsedTime = end - start
            elapsed_duration = divmod(elapsedTime.total_seconds(), 60)

            print(
                "Time elapsed: {} mins and {:.2f} secs".format(
                    elapsed_duration[0], elapsed_duration[1]
                )
            )
            #print("test_dish_id +1, dish_list[test_dish_id] ", test_dish_id +1, dish_list[test_dish_id])
            try:
                fold_result = {
                    "Fold": fold + 1,
                    "Train_Loss": train_loss,
                    "Train_Accuracy": train_accuracy,
                    "Valid_Loss": valid_loss,
                    "Valid_Accuracy": valid_accuracy,
                    "Fold_Timelapse_Minutes": elapsed_duration[0]
                }  # ,
                # "Test_Dish1_accuracy" : test_accuracy_list[0][2],
                # "Test_Dish2_accuracy" : test_accuracy_list[1][2]}
            except IndexError:
                fold_result = {
                    "Fold": fold + 1,
                    "Train_Loss": train_loss,
                    "Train_Accuracy": train_accuracy,
                    "Valid_Loss": valid_loss,
                    "Valid_Accuracy": valid_accuracy,
                    "Fold_Timelapse_Minutes": elapsed_duration[0]
                }

            fold_result_df = fold_result_df.append(fold_result, ignore_index=True)

            
            print("--------------")


        print("-------Training Finished-------\n")

        save_result_path = os.path.join(destination_folder, "fold_results_train.tsv")

        # Saving the results
        fold_result_df.to_csv(save_result_path, sep="\t", index=False, encoding="utf-8")

        print("Fold Results saved in ==>" + save_result_path)

        # Print final model statistics

        total_duration = fold_result_df["Fold_Timelapse_Minutes"].sum()
        total_duration = divmod(total_duration, 60) 
        print(f"Total training time for {num_folds} folds: {total_duration[0]}h {total_duration[1]}min" )

        #total_num_correct = fold_result_df["Correct_Predictions"].sum()
        #total_num_actions = fold_result_df["Num_Actions"].sum()
        #avg_model_accuracy = total_num_correct / total_num_actions
        #print("Total correct predictions: ", total_num_correct)
        #print("Total actions: ", total_num_actions)
        #print("Total model accuracy: ", avg_model_accuracy)
    
        #return test_dish_list




# FUNCTIONS FOR OTHER MODELS: SIMPLE, SIMILARITY, ETC.
# -----------------------------------------------------------------------------------------------------

    def basic_training(self,
                       model,
                       dish_list,
                       saved_file_path):
        
            action_pair_list = list()
        
            for dish in dish_list:
                
                data_folder = os.path.join(folder, dish)  # dish folder
                recipe_folder = os.path.join(data_folder, recipe_folder_name)  # recipe folder
        
                alignment_file_path = os.path.join(
                data_folder, alignment_file
                )  # alignment file
            
    
                # Gold Standard Alignments between all recipes for dish
                alignments = pd.read_csv(
                    alignment_file_path, sep="\t", header=0, skiprows=0, encoding="utf-8"
                    )
    
                # Group by Recipe pairs
                dish_group_alignments = alignments.groupby(["file1", "file2"])
            
                for key in dish_group_alignments.groups.keys():

                    recipe1_filename = os.path.join(recipe_folder, key[0] + ".conllu")
                    recipe2_filename = os.path.join(recipe_folder, key[1] + ".conllu")
                    
                    recipe_pair_alignment = dish_group_alignments.get_group(key)
                
                    # Generate action pairs in text format 
                    _, _, action_pairs = model.generate_action_pairs(recipe_pair_alignment, recipe1_filename, recipe2_filename)
                
                    action_pair_list.extend(action_pairs)
        
            # Generate Vocabulary of action pairs
            action_pair_vocabulary = model.generate_vocabulary(action_pair_list)
        
            # Save Vocab 
            save_vocabulary(saved_file_path, action_pair_vocabulary)

    def run_naive_folds_train( self,
        model,
        num_folds
        ):
        """
        Running 10 fold cross validation for naive baseline

        Parameters
        ----------
        model : NaiveModel object
            Naive Baseline model
        num_folds : Int

        """

        dish_list = os.listdir(folder)

        dish_list = [dish for dish in dish_list if not dish.startswith(".")]
        dish_list.sort()

        fold_result_df = pd.DataFrame(
            columns=[
                "Fold",
                "Test_Accuracy",
                "Correct_Predictions",
                "Num_Actions",
            ]
        )  # , "Test_Dish1_accuracy", "Test_Dish2_accuracy"])
        
        destination_folder = destination_folder4
        
        overall_predictions = 0
        overall_actions = 0 

        for fold in range(num_folds):

            start = datetime.now()

            saved_file_path = os.path.join(
                destination_folder, "model" + str(fold + 1) + ".pt"
            )  # Model saved path

            train_dish_list = dish_list.copy()
            print("Fold [{}/{}]".format(fold + 1, num_folds))

            print("-------Training-------")

            self.basic_training(
                model,
                train_dish_list,
                saved_file_path,
            )

                           
            overall_predictions += total_correct_predictions
            overall_actions += total_actions

            fold_result = {
                "Fold": fold + 1,
                "Test_Accuracy": test_accuracy,
                "Correct_Predictions": total_correct_predictions,
                "Num_Actions": total_actions,
            }  # ,
            # "Test_Dish1_accuracy" : test_accuracy_list[0][2],
            # "Test_Dish2_accuracy" : test_accuracy_list[1][2]}

            fold_result_df = fold_result_df.append(fold_result, ignore_index=True)

            end = datetime.now()

            elapsedTime = end - start
            elapsed_duration = divmod(elapsedTime.total_seconds(), 60)

            print(
                "Time elapsed: {} mins and {:.2f} secs".format(
                    elapsed_duration[0], elapsed_duration[1]
                )
            )
            print("--------------")
            
            
        overall_accuracy = overall_predictions * 100 / overall_actions
        
        print("Overall Model Accuracy: {:.2f}".format(overall_accuracy))
        
        fold_result = {
                "Fold": 'Overall',
                "Test_Accuracy": overall_accuracy,
                "Correct_Predictions": overall_predictions,
                "Num_Actions": overall_actions,
            }
        
        fold_result_df = fold_result_df.append(fold_result, ignore_index=True)

        save_result_path = os.path.join(destination_folder, "fold_results.tsv")
        
        results_file_path = os.path.join(
            destination_folder, "model_result.tsv"
        )  # Model saved path

        # Saving the results
        fold_result_df.to_csv(save_result_path, sep="\t", index=False, encoding="utf-8")
        

        print("Fold Results saved in ==>" + save_result_path)
        
# -------------------------------------------------------------------------------

# final part of main.py

TT = Folds_Train()  # calling the Training class

if model_name == "Alignment-with-feature":

     model = AlignmentModel(embedding_dim, HIDDEN_DIM1, HIDDEN_DIM2, OUTPUT_DIM, device).to(
         device
     )  # Out Alignment Model with features

     print(model)
     """for name, param in model.named_parameters():
         if param.requires_grad:
                 print(name)"""

     optimizer = optim.Adam(model.parameters(), lr=LR)  # optimizer for training
     criterion = nn.CrossEntropyLoss()  # Loss function

     ################ Cross Validation Folds #################

     TT.run_folds_train(
         embedding_name, 
         emb_model, tokenizer, model, optimizer, criterion, EPOCHS, FOLDS, device
     )

elif model_name == "Alignment-no-feature":

     model = AlignmentModel(
         embedding_dim, HIDDEN_DIM1, HIDDEN_DIM2, OUTPUT_DIM, device, False
     ).to(
         device
     )  # Out Alignment Model w/o features

     print(model)

     optimizer = optim.Adam(model.parameters(), lr=LR)  # optimizer for training
     criterion = nn.CrossEntropyLoss()  # Loss function

     TT.run_folds_train(
         embedding_name,
         emb_model, 
         tokenizer,
         model,
         optimizer,
         criterion,
         EPOCHS,
         FOLDS,
         device,
         False,
     )

elif model_name == "Cosine_similarity":

     cosine_similarity_model = SimpleModel(embedding_dim, device).to(device) # Simple Cosine Similarity Baseline

     print(cosine_similarity_model)

     print("-------Testing (Simple Baseline) -------")

     TT.test_simple_model(embedding_name, emb_model, tokenizer, cosine_similarity_model, device)
        
        
elif model_name == 'Naive':
        
     naive_model = NaiveModel(device) # Naive Common Action Pair Heuristics Baseline
        
     print('Common Action Pair Heuristics Model')
        
     ################ Cross Validation Folds #################
        
     TT.run_naive_folds(
         naive_model,
         FOLDS
         )
        
elif model_name == 'Sequence':
        
     sequence_model = SequenceModel()
        
     print('Sequential Alignments')
        
     sequence_model.test_sequence_model()

else:

     print(
         "Incorrect Argument: Model_name should be ['Cosine_similarity', 'Naive', 'Alignment-no-feature', 'Alignment-with-feature']"
     )


#### Saving the model parameters in a .pt file ####
#torch.save(tagger.state_dict(), "./model_parameters_tagger.pt")

# load trained model parameters again
# instantiate the saved model before using it
#trained_tagger = LSTM_model(input_size=input_size, embedding_dim=embedding_dim, hidden_size=hidden_size, vocab_size=vocab_size, number_classes=number_classes)

# load the trained parameters
#trained_tagger.load_state_dict(torch.load("./model_parameters_tagger.pt"))   
