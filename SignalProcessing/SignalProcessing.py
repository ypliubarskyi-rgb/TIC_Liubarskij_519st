import random
from abc import ABC, abstractmethod


class RockPaperScissors(ABC):
    """
            Ініціалізує гру з динамічним набором варіантів та генерує правила.
    """
    def __init__(self, options):
        self.options = options
        self.rules = self._generate_rules(options)

    def _generate_rules(self, options):
        """
                Математично вираховує, хто кого перемагає, базуючись на позиціях у списку.
                Використовує алгоритм 'половини' для створення збалансованого ігрового циклу.
        """
        rules = {}
        n = len(options)
        for i in range(n):

            current = options[i]
            reordered = options[i + 1:] + options[:i]

            half = len(reordered) // 2
            winning_against_current = reordered[:half]
            rules[current] = winning_against_current
        return rules

    @abstractmethod
    def get_bot_move(self):
        pass


class DynamicBot(RockPaperScissors):
    def get_bot_move(self):
        return random.choice(self.options)


class Game:
    """
            Ініціалізує ігровий процес з вибраним ботом та початковим рейтингом гравця.
            Встановлює стан гри на очікування введення користувача.
    """
    def __init__(self, bot: RockPaperScissors, score: int):
        self.bot = bot
        self.score = score

    def get_safe_input(self, prompt=""):
        while True:
            user_input = input(prompt).strip()
            if user_input == "!exit":
                print("Bye!")
                exit()
            elif user_input == "!rating":
                print(f"Your rating: {self.score}")
                continue

            if user_input in self.bot.options:
                return user_input
            else:
                print("Invalid input")

    def run(self):
        user_move = self.get_safe_input("> ")
        bot_move = self.bot.get_bot_move()

        if user_move == bot_move:
            print(f"There is a draw ({bot_move})")
            self.score += 50
        elif bot_move in self.bot.rules[user_move]:

            print(f"Sorry, but the computer chose {bot_move}")
        else:

            print(f"Well done. The computer chose {bot_move} and failed")
            self.score += 100


def main():

    name = input("Enter your name: ")
    print(f"Hello, {name}")




    user_score = 0
    try:
        with open("rating.txt", "r", encoding="utf-8") as file:
            for line in file:
                parts = line.split()
                if parts and parts[0] == name:
                    user_score = int(parts[1])
                    break
    except FileNotFoundError:
        pass


    raw_options = input().strip()
    if not raw_options:
        options = ["rock", "paper", "scissors"]
    else:
        options = raw_options.split(",")

    print("Okay, let's start")


    bot = DynamicBot(options)
    game = Game(bot, user_score)

    while True:
        game.run()


if __name__ == '__main__':
    main()