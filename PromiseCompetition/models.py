from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

doc = """
This experiment is a promise game and a dictator game in random order and includes control questions as well as a questionnaire. Author: Andreas Born
"""


class Constants(BaseConstants):
    name_in_url = 'CompetingPromises'
    players_per_group = 3
    num_rounds = 11
    instructions2_template = 'CompetingPromises/Instructions2.html'
    instructions1_template = 'CompetingPromises/Instructions1.html'
    instructions3_template = 'CompetingPromises/Instructions3.html'
    endowment = 100
    multiplier = 2
    # correct answers to the control questions
    controlq1 = 4
    controlq2 = 2
    controlq3 = 3
    controlq4 = 3
    # not included
    controlq5 = 4

class Subsession(BaseSubsession):
    receiver = models.IntegerField()
    def creating_session(self):
        #randomize the number of the receiver for promise game each subsession
        random.seed()
        self.receiver=random.randrange(1, 4, 1)
        #assign treatments (whether to play dicator game first or second) if it is the first round
        if self.round_number == 1:
            # if no specific number of treatment 1 groups required assign groups and treatment randomly
            if self.session.config['treatment_1_num'] == -1:
                self.group_randomly()
                for p in self.get_players():
                    if p.group_id % 2 == 0:
                        p.participant.vars['treatment'] = 1
                    else:
                        p.participant.vars['treatment'] = 2
            else:#if sepcific number of T1 groups required assign these and assign treatment 2 to the remaining groups
                players = self.get_players()
                pool = {p for p in players}
                group_matrix = []
                count_t1 = 0
                while pool:
                    if count_t1 < self.session.config['treatment_1_num']:
                        pool.pop().participant.vars['treatment'] = 1
                        pool.pop().participant.vars['treatment'] = 1
                        pool.pop().participant.vars['treatment'] = 1
                        count_t1 += 1
                    else:
                        pool.pop().participant.vars['treatment'] = 2
                        pool.pop().participant.vars['treatment'] = 2
                        pool.pop().participant.vars['treatment'] = 2
            for p in self.get_players(): # determine the round for which the participant is paid
                random.seed()
                p.participant.vars['paid_round'] = random.randint(1, Constants.num_rounds)
                                    # create the dictator pay variable in the participant table
                p.participant.vars['dict_contribution'] = -1

        #copy the treatment into the player table for the according round
        for p in self.get_players():
            p.treatment = p.participant.vars['treatment']
            p.session_id = p.participant.id_in_session
            #only update the dict contribution after they have been created to avoid having a default value
            #if p.treatment != 1:
            #    p.dict_contribution = p.in_round(1).dict_contribution


        # randomize the groups
        if self.round_number < Constants.num_rounds and self.round_number != 1:
            self.group_randomly()

        else:  # in turn 1 and the last turn groups have to consist of participants with the same treatment
            players = self.get_players()
            T1_players = [p for p in players if p.participant.vars['treatment'] == 1]
            T2_players = [p for p in players if p.participant.vars['treatment'] == 2]
            group_matrix = []
            # pop elements from M_players until it's empty
            while T1_players:
                new_group = [
                    T1_players.pop(),
                    T1_players.pop(),
                    T1_players.pop(),
                ]
                group_matrix.append(new_group)
            while T2_players:
                new_group = [
                    T2_players.pop(),
                    T2_players.pop(),
                    T2_players.pop(),
                ]
                group_matrix.append(new_group)
            self.set_group_matrix(group_matrix)

        for p in self.get_players():
            # determine if subject is receiver for dictator game
            if ((p.subsession.round_number == 1) and (p.participant.vars['treatment'] == 2)) or (
                    (p.subsession.round_number == Constants.num_rounds) and (p.participant.vars['treatment'] == 1)):
                random.seed()
                p.is_receiver = random.randrange(0,2,1)



    def dictator_teams(self):
        pool1 = [p for p in self.get_players()]
        pool2 = [p for p in self.get_players()]

        if len(pool1) % 2 == 0:
            while pool1:
                p1 = pool1.pop()
                p1.is_receiver = 0

                p2 = pool1.pop()
                p2.is_receiver = 1
                p2.dictator_received = p1.dict_contribution

        else:  #uneven number of players, deterining first player as receiver who gets points from second player before usual procedure
            p1 = pool1.pop()
            p1.is_receiver = 1

            pool2.pop()
            p2 = pool2.pop()

            p1.dictator_received = p2.dict_contribution
            while pool1:
                p1 = pool1.pop()
                p1.is_receiver = 0

                p2 = pool1.pop()
                p2.is_receiver = 1
                p2.dictator_received = p1.dict_contribution

class Group(BaseGroup):
        promise1 = models.IntegerField(min=0, max=Constants.endowment, initial=0)
        promise2 = models.IntegerField(min=0, max=Constants.endowment, initial=0)
        promise3 = models.IntegerField(min=0, max=Constants.endowment, initial=0)
        contribution1 = models.IntegerField(min=0, max=Constants.endowment, initial=0)
        contribution2 = models.IntegerField(min=0, max=Constants.endowment, initial=0)
        contribution3 = models.IntegerField(min=0, max=Constants.endowment, initial=0)
        choice=models.IntegerField()

class Player(BasePlayer):

        promise = models.IntegerField(min=0, max=Constants.endowment, label="Please enter the number of points you want to promise")
        contribution = models.IntegerField(min=0, max=Constants.endowment, label="Please enter the number of points you want to send")
        dict_contribution = models.IntegerField(min=0, max=Constants.endowment, label="Please enter the number of points you want to send")
        dictator_received = models.IntegerField(initial = 0)
        received = models.CurrencyField(initial = 0)
        choice = models.IntegerField()
        round_pay = models.IntegerField()
        is_receiver = models.IntegerField(initial = -1)
        treatment = models.IntegerField()
        round_pay_dict = models.IntegerField()

        controlq1 = models.IntegerField(min=1, max=4, widget=widgets.RadioSelect, label="Can you earn money in addition to the participation payment?", choices=[
            [1, "No, I only get the participation payment."], [2,"Yes, I earn 10 cents per point for the points I get in all rounds."], [3,"Yes, I earn 5 cents for the sum of the points I get in all rounds."], [4, "Yes, I earn 10 cents per point for the points I get in one randomly chosen round."], [5,"Yes, I earn 5 cents per pointfor the points I get in one randomly chosen round."]
        ])
        controlq2 = models.IntegerField(min=1, max=4, widget=widgets.RadioSelect, label="If a sender sends 50 points to the receiver, how many points does the receiver get?", choices=[
            [1, "The receiver gets 0 points."], [2, "The receiver gets 100 points, as all points sent are multiplied by 2."], [3, "The receiver gets 50 points."], [4, "The receiver gets 25 points, as the points are multiplied by 0.5."]
        ])
        controlq3 = models.IntegerField(min=1, max=4, widget=widgets.RadioSelect, label="Which of the following is true?", choices=[
            [1, "In each round of the experiment, I will EITHER make decisions as a sender or as a receiver. The computer will randomly determine which role I take each round."], [2, "In each round of the experiment, I will make decisions as sender AND as receiver. Both will be implemented."], [3, "In each round of the experiment, I will make decisions as sender AND as receiver. In the end of each round, the computer randomly decides which role I take. Only the corresponding decision will be implemented."], [4, "In each round of the experiment, I will make decisions as a sender AND a receiver. In the first round the computer determines my role and implement the corresponding decision in ALL following rounds."]
        ])
        controlq4 = models.IntegerField(min=1, max=4, widget=widgets.RadioSelect, label="Will you interact with the same participants each round?", choices=[
            [1, "Yes, I will always interact with the same participants."], [2, "No, but within each of the two parts of the experiment I will interact with the same participants."], [3, "No, in each round of the two parts I will interact with random participants."]
        ])
        controlq5 = models.IntegerField(min=1, max=4, widget=widgets.RadioSelect, label="Will the computer autmatically promise you make as your decision?", choices=[
            [1, "Yes, if I get selected by the receiver."], [2,"Yes, always."], [3, "Only if I choose not to break it."], [4, "No, after I make the promise I get to indicate my choice in a separate step."]
        ])
        question1 = models.IntegerField(min=18, max=50, label="What is your age?")
        question2 = models.IntegerField(label="What gender do you identify as?", choices=[[1, "female"], [2, "male"], [3, "other"]])
        question3 = models.StringField(label="What is your major?")
        question4 = models.LongStringField(label="Did you incur any problems or questions during the experiment that"
                                                 " could not be resolved? If yes, please describe!")
        question5 = models.LongStringField(label="What was your rationale for the promises you made?")
        question6 = models.LongStringField(label="What was your rational your decision to select a promises?")

        def get_partners(self):
            return str(self.get_others_in_group())

        def get_id(self):
            return self.id_in_group


        def update_dictator(self):
            if (self.treatment == 2 and self.round_number!=1):
                self.dict_contribution = self.in_round(1).dict_contribution

        def determine_round_pay(self):
            #Payoff for promise game
            self.round_pay = 0
            if ((self.round_number != 1) and (self.participant.vars['treatment'] == 2)) or ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)):
                if self.id_in_group == self.subsession.receiver:
                    exec("self.round_pay = self.group.contribution" + str(self.group.choice)
                         + " * Constants.multiplier")
                else:
                    if self.id_in_group == self.group.choice:
                        exec("self.round_pay = Constants.endowment - self.group.contribution" + str(self.group.choice))
            # Payoff for Dictator Game
            #else:
            #    if self.is_receiver == 1:
            #        # In the dictator round each individual receives from the individual with the next higher in-group id (or the lowest)
            #        try:
            #            exec("self.round_pay = self.group.contribution" + str(self.id_in_group % 3 + 1)
            #                 + " * Constants.multiplier")
            #        except:
            #            self.round_pay = self.group.contribution1 * Constants.multiplier
            #    else:
            #        self.round_pay = Constants.endowment - self.dict_contribution

            if self.round_number == Constants.num_rounds:
                if self.is_receiver == 1:
                    self.round_pay_dict = self.dictator_received * Constants.multiplier
                else:
                    self.round_pay_dict = Constants.endowment - self.dict_contribution
            return self.round_pay


        def make_payment(self):
            if (self.participant.vars['paid_round'] == 1 and self.treatment == 2) or (self.participant.vars['paid_round'] == Constants.num_rounds and self.treatment == 1):
                self.payoff = c(self.round_pay_dict)
            else:
                try:
                    self.payoff = c(self.in_round(self.participant.vars['paid_round']).round_pay)
                except:
                    self.payoff = c(self.in_round(2).round_pay)
            return self.participant.vars['paid_round']


