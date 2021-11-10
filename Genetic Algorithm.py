# Christian Chapman
# CS 461 - Intro to AI
# Project 2 - Genetic Algorithm
# 10/24/21
import random
import matplotlib.pyplot as plt

def getInputData(fileName):
    with open(fileName) as inputFile:
        fileTokens = inputFile.readlines()
        fileTokens = [token.split("\t") for token in fileTokens]
        return fileTokens


def generateIndicies():
    indicies = []
    for i in range(20):
        randInteger = random.randint(0, 399)
        while randInteger in indicies:
            randInteger = random.randint(0, 399)

        indicies.append(randInteger)

    return indicies


def initRandomValues(population):
    for indiv in population:
        indicies = generateIndicies()
        for i in range(400):
            if i in indicies:
                indiv[i] = 1

    return population


def calcFitness(indiv, inputData):
    score = 0
    weight = 0
    for i in range(400):
        if indiv[i]:
            score += float(inputData[i][0])
            weight += float(inputData[i][1])

    if weight > 500:
        score = 1

    score = round(score, 2)

    return score


def calcTotalFitnesses(population, inputData):
    fitnesses = []

    for i in range(populationSize):
        fitScore = calcFitness(population[i], inputData)
        fitnesses.append(fitScore)

    return fitnesses


def createCDF(fitnesses):
    l2_transformation = [x ** 2 for x in fitnesses]
    l2_sum = sum(l2_transformation)

    cdf = []
    cdfSum = 0
    for l2 in l2_transformation:
        cdfSum += l2
        cdf.append(cdfSum / l2_sum)

    return cdf


def applyMutation(indiv):
    # 1 in 10,000 chance of applying a mutation to one random bit of the population member
    if random.randint(1, 10000) == 1:
        mutationIdx = random.randint(0, 399)

        if indiv[mutationIdx]:  # if it is 1
            indiv[mutationIdx] = 0  # switch it to 0

        else:
            indiv[mutationIdx] = 1  # else, switch to 1

    return indiv


def newGeneration(population, cdf):
    newPopulation = []
    for i in range(len(population) // 2):
        randProb1 = random.uniform(0, 1)
        randProb2 = random.uniform(0, 1)

        # Initializing population individuals that will match with the probabilities generated above
        indiv1 = []
        indiv2 = []

        for j in range(len(cdf)):
            if cdf[j] > randProb1:
                indiv1 = population[j]
                break

        for j in range(len(cdf)):
            if cdf[j] > randProb2:
                indiv2 = population[j]
                break

        child1 = []
        child2 = []
        sliceIdx = random.randint(1, 398)

        child1 = indiv1[:sliceIdx] + indiv2[sliceIdx:]
        child2 = indiv2[:sliceIdx] + indiv1[sliceIdx:]

        child1 = applyMutation(child1)
        child2 = applyMutation(child2)

        newPopulation.append(child1)
        newPopulation.append(child2)

    return newPopulation


def isPopulationGrowing(avgFitness):
    counter = 0

    try:

        for i in range(-1, -11, -1):  # counting backwards
            prcnt = (avgFitness[i - 1] / avgFitness[i]) * 100
            prcnt = 100 - prcnt

            if prcnt < 1.0:
                counter += 1
            else:
                counter = 0

        if counter == 10:
            return False
        else:
            return True

    except IndexError:  # less than 10 generations have been created, too soon to tell
        return True


def outputAvgFitnesses(avgFitnesses):
    avgFitnessOutput = open("Average Fitness Scores.txt", "w")
    avgFitnessOutput.write("\n".join([str(x) for x in avgFitnesses])) # converting list to list of strings to be able to output to file
    avgFitnessOutput.close()


def outputMaxFitness(population, fitnesses, inputData):
    maxFitness = max(fitnesses)
    maxFitnessIndex = fitnesses.index(maxFitness)
    totalWeight = 0

    outputString = "Highest fitness selection found: {}\n".format(maxFitness)

    for i in range(len(population[maxFitnessIndex])):
        if population[maxFitnessIndex][i]:
            totalWeight += float(inputData[i][1])

    outputString += "Total weight of this selection: {:.2f}\n".format(totalWeight)

    outputString += "\nBelow are the selected items:\n"
    for i in range(len(population[maxFitnessIndex])):
        if population[maxFitnessIndex][i]:
            outputString += "Item {} was taken\n".format(i + 1)

    maxFitnessOutput = open("Max Fitness Selection Details.txt", "w")
    maxFitnessOutput.write(outputString)
    maxFitnessOutput.close()


if __name__ == "__main__":
    fileName = ""
    fileError = True

    while fileError:
        try:
            fileName = input("Enter the name of the input file: ")
            file = open(fileName)
            file.close()
            fileError = False

        except FileNotFoundError:
            print("Error: File not found. Please try again.")

    valError = True
    while valError:
        try:
            populationSize = int(input("Enter the desired population size: "))
            valError = False
        except ValueError:
            print("Error: Please enter an integer")

    print("Please select one of the following options:",
          "1. Continue iterating until the average fitness scores improve less than 1% across 10 consecutive generations",
          "2. Continue iterating until a desired number of generations",
          sep="\n")

    userOption = 0
    while userOption not in [1, 2]:
        try:
            userOption = int(input())
            if userOption not in [1, 2]:
                print("\nInvalid input. Please enter a valid option")

        except ValueError:
            print("\nInvalid input. Please enter a valid option")

    maxGenerations = 0
    if userOption == 2:

        valError = True
        while valError:
            try:
                maxGenerations = int(input("Enter the max number of generations: "))
                valError = False

            except ValueError:
                print("\nInvalid input.")

    inputData = getInputData(fileName)

    # initializes a 2D list for the population where each nested list is a list of 400 0's
    population = [[0 for j in range(400)] for i in range(populationSize)]

    population = initRandomValues(population)
    fitnesses = calcTotalFitnesses(population, inputData)

    avgFitnesses = []
    avgFitnesses.append(round(sum(fitnesses) / len(fitnesses), 2))

    cdf = createCDF(fitnesses)

    genNum = 1

    print("Avg Fitness Score\tGeneration Number")

    print(avgFitnesses[-1], genNum, sep="\t\t\t\t")

    if (userOption == 1):
        while isPopulationGrowing(avgFitnesses):
            genNum += 1
            population = newGeneration(population, cdf)

            fitnesses = calcTotalFitnesses(population, inputData)

            avgFitnesses.append(round(sum(fitnesses) / len(fitnesses), 2))

            cdf = createCDF(fitnesses)

            if genNum % 50 == 0 or genNum <= 5:
                print(avgFitnesses[-1], genNum, sep="\t\t\t\t")

    else:
        while genNum < maxGenerations:
            genNum += 1
            population = newGeneration(population, cdf)

            fitnesses = calcTotalFitnesses(population, inputData)

            avgFitnesses.append(round(sum(fitnesses) / len(fitnesses), 2))

            cdf = createCDF(fitnesses)

            if genNum % 50 == 0 or genNum <= 5:
                print(avgFitnesses[-1], genNum, sep="\t\t\t\t")

    outputAvgFitnesses(avgFitnesses)
    outputMaxFitness(population, fitnesses, inputData)

    print("\n\nOutput files generated successfully")

    plt.plot(avgFitnesses)
    plt.ylabel("Average Fitness Score")
    plt.xlabel("Generation")
    plt.show()

