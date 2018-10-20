from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class StartPage(Page):
    def is_displayed(self):
        #return False
        return self.round_number == 1

class Introduction1(Page):
    def is_displayed(self):

        #return False
        return ((self.round_number == 1) and (self.participant.vars['treatment'] == 2))

class Introduction2(Page):
    def is_displayed(self):
        #return False

        return ((self.round_number == 1) and (self.participant.vars['treatment'] == 1))

class ControlQuestions(Page):
    def is_displayed(self):
        #return False
        return self.round_number == 1
    def vars_for_template(self):
        return {
            'treatment': self.participant.vars['treatment'],
                }
    form_model = 'player'
    form_fields = ['controlq1', 'controlq2', 'controlq3', 'controlq4']
    def error_message(self, values):
        if values["controlq1"] != Constants.controlq1:
            return 'You made at least one mistake, please control question 1 again!'
        if values["controlq2"] != Constants.controlq2:
            return 'You made at least one mistake, please control question 2 again!'
        if values["controlq3"] != Constants.controlq3:
            return 'You made at least one mistake, please control question 3 again!'
        if values["controlq4"] != Constants.controlq4:
            return 'You made at least one mistake, please control question 4 again!'



class StartWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == 1
    title_text = "Please wait for the other participants!"
    body_text = 'The experiment will start once all participants are ready.'

class Round_start(Page):
    def is_displayed(self):
        return ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number != 1) and (self.participant.vars['treatment'] == 2))

    def vars_for_template(self):
        return {'round': self.group.round_number - self.participant.vars['treatment'] + 1,
                'treatment': self.participant.vars['treatment'],
                }
    def before_next_page(self):
        self.player.update_dictator()

class Round_start_dic(Page):
    def is_displayed(self):
        return ((self.round_number == Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number == 1) and (self.participant.vars['treatment'] == 2))

    def vars_for_template(self):
        return {'round': self.group.round_number - self.participant.vars['treatment'] + 1,
                'treatment': self.participant.vars['treatment'],
                }

class ShuffleWaitPage(WaitPage):

    def is_displayed(self):
        return self.round_number == 2
    title_text = "Please wait for the other participants!"
    body_text = 'The experiment will continue once all participants are ready.'
    wait_for_all_groups = True

class Dictator(Page):
    def is_displayed(self):
        return ((self.round_number == Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number == 1) and (self.participant.vars['treatment'] == 2))

    def vars_for_template(self):
        return {'endowment': Constants.endowment, 'multiplier': Constants.multiplier, 'treatment': self.participant.vars['treatment']}

    form_model = 'player'
    form_fields = ['dict_contribution']

    def before_next_page(self):
        if self.player.get_id() == 1:
            self.group.contribution1 = self.player.dict_contribution
        elif self.player.get_id() == 2:
            self.group.contribution2 = self.player.dict_contribution
        else:
            self.group.contribution3 = self.player.dict_contribution
        self.player.participant.vars['dict_contribution'] = self.player.dict_contribution



class Promise(Page):
    def is_displayed(self):
        return ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number != 1) and (self.participant.vars['treatment'] == 2))

    def vars_for_template(self):
        return {'endowment': Constants.endowment, 'multiplier': Constants.multiplier}
    form_model = 'player'
    form_fields = ['promise']
    def before_next_page(self):
        if self.player.get_id() == 1:
            self.group.promise1=self.player.promise
        elif self.player.get_id() == 2:
            self.group.promise2 = self.player.promise
        else:
            self.group.promise3 = self.player.promise

class PromiseWaitPage(WaitPage):
    def is_displayed(self):
        return ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number != 1) and (self.participant.vars['treatment'] == 2))
    title_text = "Please wait."
    body_text = "Please wait for the other participants to make their decisions."
    wait_for_all_groups = False

class Contributions(Page):
    def is_displayed(self):
        return ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number != 1) and (self.participant.vars['treatment'] == 2))

    def vars_for_template(self):
        return {'endowment': Constants.endowment, 'multiplier': Constants.multiplier}

    form_model = 'player'
    form_fields = ['contribution']

    def before_next_page(self):
        if self.player.get_id() == 1:
            self.group.contribution1 = self.player.contribution
        elif self.player.get_id() == 2:
            self.group.contribution2 = self.player.contribution
        else:
            self.group.contribution3 = self.player.contribution


class Receiver(Page):
    def is_displayed(self):
        return ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number != 1) and (self.participant.vars['treatment'] == 2))

    def vars_for_template(self):
        return {'round': self.group.round_number + 1 - self.participant.vars['treatment']}


class Prom_Choice(Page):
    def is_displayed(self):
        return ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number != 1) and (self.participant.vars['treatment'] == 2))

    """Displays the promises of the other two players to each player"""
    form_model = 'player'
    form_fields = ['choice']
    def vars_for_template(self):
        return {
                'own_id': self.player.id_in_group,
                'promise1': self.group.promise1,
                'promise2': self.group.promise2,
                'promise3': self.group.promise3
                }
    def before_next_page(self):
        if self.player.get_id() == self.subsession.receiver:
            self.group.choice = self.player.choice


class ResultWaitPage(WaitPage):
    pass


class Result(Page):
    def is_displayed(self):
        return ((self.round_number != Constants.num_rounds) and (self.participant.vars['treatment'] == 1)) or ((self.round_number != 1) and (self.participant.vars['treatment'] == 2))
    def vars_for_template(self):
        choice = self.group.choice
        prom_chosen = exec("self.group.promise" + str(choice))
        return {
            'own_id': self.player.id_in_group,
            'choice': choice,
            'receiver': self.subsession.receiver,
            'promise1': self.group.promise1,
            'promise2': self.group.promise2,
            'promise3': self.group.promise3,
            'prom_chosen': prom_chosen,
            'contribution1': self.group.contribution1,
            'contribution2': self.group.contribution2,
            'contribution3': self.group.contribution3,
            'prom_not_chosen': exec("self.group.promise" + str({1, 2, 3}.symmetric_difference({self.group.choice, self.subsession.receiver}).pop())),
            'endowment': Constants.endowment,
            'multiplier': Constants.multiplier,
            'round': self.group.round_number + 1 - self.participant.vars['treatment'],
            'treatment': self.participant.vars['treatment'],
            'round_pay': self.player.determine_round_pay(),
        }
    def before_next_page(self):
        self.player.determine_round_pay()

class CalcWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds
    wait_for_all_groups = True
    def after_all_players_arrive(self):
        self.subsession.dictator_teams()


class DictatorResult(Page):
    def is_displayed(self):
        return (self.round_number == Constants.num_rounds)
    def vars_for_template(self):
        return {
            'own_id': self.player.id_in_group,
            'receiver': self.player.is_receiver,
            'contribution1': self.group.contribution1,
            'contribution2': self.group.contribution2,
            'contribution3': self.group.contribution3,
            'endowment': Constants.endowment,
            'multiplier': Constants.multiplier,
            'treatment': self.participant.vars['treatment'],
            'round_pay': self.player.round_pay,
        }
    def before_next_page(self):
        self.player.determine_round_pay()




class Questionnaire(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    form_model = 'player'
    form_fields = ['question1', 'question2', 'question3', 'question4', 'question5', 'question6']
    def before_next_page(self):
       self.player.make_payment()





class FinalPage(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        return {
            'pay_round': self.participant.vars['paid_round'],
            'you_earn': self.participant.payoff_plus_participation_fee(),
        }





page_sequence = [
    StartPage,
    Introduction1,
    Introduction2,
    ControlQuestions,
    StartWaitPage,
    ShuffleWaitPage,
    Round_start,
    Round_start_dic,
    Dictator,
    Promise,
    Contributions,
    PromiseWaitPage,
    Receiver,
    Prom_Choice,
    ResultWaitPage,
    Result,
    CalcWaitPage,
    DictatorResult,
    Questionnaire,
    FinalPage,
]
