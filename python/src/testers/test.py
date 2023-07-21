from src.coverers.data_structs import * 
from src.coverers.line import * 
from src.readers.reader import *
from src.coverers.wedgecover import *
import numpy as np 
import matplotlib.pyplot as plt 

def wedge_test(lining:str = "makePatches_Projective", apexZ0 = 0, z0 = np.arange(-15, 15.5, 0.5), ppl = 16, wedges = [0, 128], lines=1000, v = 'v3', accept_cutoff = 10., uniform_N_points = False, savefig=False):
    """Creates acceptance vs z0 plot
    
    Args:
        lining (str, optional): solving method, default is solveS
        apexZ0 (int, optional): the z values the patches are being made in accordance to
        z0 (num or list, optional): array of z0 values we are testing over, default is range of -15 to 15 with 0.5 spacing
        n (int, optional): ppl (point per patch per layer), default is 16
        wedges (list, optional): which wedges, enter in list of [starting wedge, ending wedge]
        lines (int, optional): how many line to test acceptance with at each z0 value
        savefig (bool, optional): True to save figure
        uniform_N_points(False or int): number of points in each layer or False to be not uniform
        v (str, optional): version of data, ensure data file is in directory as "wedgeData_{v}_128.txt"
    """

    #create list for z values we're testing the acceptance of, number of covers, and PRF
    mean_list = np.zeros(( wedges[1]-wedges[0], len(z0)))
    num_covers = []
    PRF = []
    data_string = f'{v} events'
    if uniform_N_points != False:
        data_string = f'Uniform {uniform_N_points} points'
        wedges = [0, 1]

    #read wedgeData file and create environment
    all_data = readFile(f'data/wedgeData_{v}_128.txt', wedges[1])
    #loop through all events
    for ik, k in enumerate(np.arange(wedges[0], wedges[1])):
        #convert to existing data format
        env, points = all_data[k] 
        data = DataSet(env)
        if uniform_N_points == False:
            data.importData(points)
        else:
            data.generateUniform([uniform_N_points, uniform_N_points, uniform_N_points, uniform_N_points, uniform_N_points])
        #add the 0.1 cm points
        data.add()
        #solve for cover
        cover = wedgeCover(env, data)
        cover.solve(apexZ0 = apexZ0, lining=lining, ppl = ppl, show = False)
        #append number of covers in the patch
        num_covers.append(cover.n_patches)
        out = [] 

        #these loops calculate PRF
        for layer in range(env.num_layers): 
            for point in data.array[layer]: 
                
                num_in = 0
                for patch in cover.patches: 
                    if patch.contains_p(point, layer): 
                        num_in += 1
                        
                out.append(num_in)
        PRF.append(out)

        #these loops calculate line acceptance
        for iz, z in enumerate(np.array(z0)):
            percentage_accepted = 0 
                
            lg = LineGenerator(env, z)
            test_lines = lg.generateEvenGrid(lines)
            
            for i in range(len(test_lines)): 
                for patch in cover.patches:
                    if patch.contains(test_lines[i]):
                        percentage_accepted += 1 
                        break

            
            percentage_accepted = percentage_accepted/lines
            mean_list[ik, iz] = mean_list[ik, iz] + percentage_accepted
    
    mean_num = format(np.mean(num_covers), ".1f")
    std_num = format(np.std(num_covers), ".1f")

    #sets minimum for plot
    if type(apexZ0) == float:
        ymin = 0
    elif type(apexZ0) == int:
        ymin = 0
    else:
        ymin = 0.9

    #creates plots and saves them
    plt.scatter(z0, np.mean(mean_list, axis = 0), color = 'r', s = 10)
    plt.plot(z0, np.mean(mean_list, axis = 0), color = 'k')
    plt.xlabel('z0 offset [cm]', fontsize = 16)
    plt.ylabel('Acceptance',  fontsize = 16)
    plt.ylim(ymin, 1.0)
    plt.title(f'{lining}', fontsize = 16)
    mask = np.abs(z0) <= accept_cutoff
    PRFm = format(np.mean(out), '.2f')
    PRFs = format(np.std(out), '.2f')
    plt.legend([f"Number of Patches: {mean_num}" + r'$\pm$' + f"{std_num}\nPoint Repetition Factor: {PRFm}" + r'$\pm$' + f"{PRFs}\n" + r'$apexZ_0$' + f" = {apexZ0}, ppl = {ppl}\n" + r'$N_{wedges}$ ' + f"= {wedges[1]}, {data_string}\nAverage Acceptance [-{accept_cutoff}, {accept_cutoff}]: {np.round(np.mean(mean_list[:, mask])*100, 2)}%"],
        loc = 8, fontsize = 12)
    if savefig == True:
        try:
            at = len(apexZ0)
        except:
            at = 0
        plt.savefig(f"Figures/wedge_test({lining}_{data_string}_{at}_ppl{ppl})")
    plt.show()

def z099(lining:str = "makePatches_Projective", accept = 0.999, start = 'odd', ppl = 16, wedges = [0, 128], v = 'v3', savefig = False):
    if start == 'odd':
        apexZ0 = [0]
        real_solve = [0]
    else:
        apexZ0 = []
        real_solve = []     
    reached = False
    z0 = np.arange(-15, 15.5, 0.5)
    lines = 1000
    left_index = 0
    right_index = 60
    last_left = 30
    last_right = 31
    data_string = f"{v} events"
    rf = False
    lf = False


    while reached == False:
        mean_list = np.zeros((len(z0), wedges[1]-wedges[0]))
        num_covers = []
        PRF = []
        file = f'data/wedgeData_{v}_128.txt'
        all_data = readFile(file, wedges[1])

        for ik, k in enumerate(np.arange(wedges[0], wedges[1])):
            env, points = all_data[k] 
            data = DataSet(env)
            data.importData(points)
            #add the 0.1 cm points
            data.add()
            #solve for cover
            cover = wedgeCover(env, data)
            cover.solve(apexZ0 = apexZ0, lining=lining, ppl = ppl, show = False)
            num_covers.append(cover.n_patches)
            out = [] 

            for layer in range(env.num_layers): 
                for point in data.array[layer]: 
                    
                    num_in = 0
                    for patch in cover.patches: 
                        if patch.contains_p(point, layer): 
                            num_in += 1
                            
                    out.append(num_in)
            PRF.append(out)

            for iz, z in enumerate(np.array(z0)):
                percentage_accepted = 0 
                    
                lg = LineGenerator(env, z)
                test_lines = lg.generateEvenGrid(lines)
                
                for i in range(len(test_lines)): 
                    for patch in cover.patches:
                        if patch.contains(test_lines[i]): 
                            percentage_accepted += 1 
                            break 

                
                percentage_accepted = percentage_accepted/lines
                mean_list[iz, ik] = mean_list[iz, ik] + percentage_accepted
        z0_means = np.mean(mean_list, axis = 1)
        if np.all(z0_means > accept):
            break
        if np.all(z0_means[left_index:last_left] > accept):
            real_solve = np.append(real_solve, [z0[left_index]])
            print('new left', z0[left_index])
            last_left = left_index
            left_index = -1
        if np.all(z0_means[last_right:right_index] > accept):
            real_solve = np.append(real_solve, [z0[right_index]])
            print('new right', z0[right_index])
            last_right = right_index
            right_index = 61
        left_index +=1
        right_index -=1
        real_solve = np.unique(real_solve)
        apexZ0 = np.copy(real_solve)

        apexZ0 = np.append(apexZ0, z0[left_index])
        apexZ0 = np.append(apexZ0,z0[right_index])
        apexZ0 = np.unique(apexZ0)
        print(left_index)
        print(right_index)
        print(np.sort(real_solve))

    ymin = accept
    mean_num = format(np.mean(num_covers), ".1f")
    std_num = format(np.std(num_covers), ".1f")

    plt.scatter(z0, np.mean(mean_list, axis = 1), color = 'r', s = 10)
    plt.plot(z0, np.mean(mean_list, axis = 1), color = 'k')
    plt.xlabel('z0 offset [cm]', fontsize = 16)
    plt.ylabel('Acceptance',  fontsize = 16)
    plt.ylim(ymin, 1.0)
    plt.title(f'{lining}', fontsize = 16)
    PRFm = format(np.mean(out), '.2f')
    PRFs = format(np.std(out), '.2f')
    plt.legend([f"Number of Patches: {mean_num}" + r'$\pm$' + f"{std_num}\nPoint Repetition Factor: {PRFm}" + r'$\pm$' + f"{PRFs}\n" + r'$apexZ_0$' + f" = {apexZ0}, ppl = {ppl}\n" + r'$N_{wedges}$ ' + f"= {wedges[1]}, {data_string}\nAverage Acceptance: {np.round(np.mean(mean_list)*100, 2)}%"],
        loc = 8, fontsize = 12)
    if savefig == True:
        try:
            at = len(apexZ0)
        except:
            at = apexZ0
        plt.savefig(f"Figures/minimal_z0_{start}_({lining}_{data_string}_ppl{16})")
    plt.show()

def numCovers(lining:str = "makePatches_Projective", events=1000, apexZ0 = 0, ppl = 16, savefig=False, v = 'v3'): 
    """Returns histogram of the number of patches

    Args:
        lining (str, optional): Solving method. Defaults to "makePatches_Projective".
        events (int, optional): number of wedges. Defaults to 1000.
        apexZ0 (num or list, optional): z0 locations patches are generated at. Defaults to 0.
        n (int, optional): points per patch per layer. Defaults to 16.
        savefig (bool, optional): Saves figure in Figures folder if True. Defaults to False.
        v (str, optional): Data version type. Defaults to 'v3'.
    """
    num_covers = [] 
    file = f'data/wedgeData_{v}_128.txt'
    all_data = readFile(file, events)
    for k in range(events): 
        env, points = all_data[k] 
        data = DataSet(env)
        data.importData(points)
        #add the 0.1 cm points
        data.add()
        #solve for cover
        cover = wedgeCover(env, data)
        cover.solve(apexZ0 = apexZ0, lining=lining, ppll = ppl, show = False)
        
        num_covers.append(cover.n_patches)
    avg = np.mean(num_covers)
    std = np.std(num_covers)
    plt.hist(num_covers, 
                bins=np.arange(np.min(num_covers), np.max(num_covers)+2)-0.5,
                edgecolor='black', 
                rwidth=0.8, label = f"mean: {format(avg, '.2f')}, stdev: {format(std, '.2f')}"
            )
    print(f"({lining}) - {format(avg, '.2f')}, {format(std, '.2f')}")
    plt.title(f"Number of Patches per Cover ({lining})", fontsize = '20')
    plt.xlabel("Number of Patches", fontsize = '16')
    plt.ylabel("Number of Covers", fontsize = '16')
    plt.legend(fontsize = '20')
    if savefig == True: 
        plt.savefig(f"Figures/nPatches_({lining})")
    plt.show()    
    
def acceptSlopePlot(lining:str = "makePatches_Projective", events=128, lines=1000, z0= 0, ppl = 16, apexZ0=0, v = 'v3', savefig=False, show = True):
    """Generates plot of acceptance for a given z0 value

    Args:
        lining (str, optional): Solving method. Defaults to "makePatches_Projective".
        events (int, optional): number of wedges. Defaults to 128.
        lines (int, optional): Number of lines tested. Defaults to 1000.
        z0 (num, optional): Where lines are coming from on z axis. Defaults to 0.
        n (int, optional): points per patch per layer. Defaults to 16.
        apexZ0 (num or list, optional): z0 locations patches are generated at. Defaults to 0.
        v (str, optional): data version. Defaults to 'v3'.
        savefig (bool, optional): Saves figure in Figures folder if True. Defaults to False.
        show (bool, optional): Set to False to just return acceptance list without plot. Defaults to True.

    Returns:
        list: Acceptance list
    """
    
    percentage_accepted = [0 for _ in range(lines)] 
    file = f'data/wedgeData_{v}_128.txt'
    all_data = readFile(file, events)
    
    for k in range(events): 
        env, points = all_data[k] 
        data = DataSet(env)
        data.importData(points)
        #add the 0.1 cm points
        data.add()
        #solve for cover
        cover = wedgeCover(env, data)
        cover.solve(lining=lining, apexZ0 = apexZ0, ppl = ppl, show = False)
        
        lg = LineGenerator(env, z0)
        test_lines = lg.generateEvenGrid(lines)
        co_tan = []
        
        
        for i in range(len(test_lines)): 
            color = "r"
            co_tan.append(100/test_lines[i].slope)
            for patch in cover.patches: 
                if patch.contains(test_lines[i]): 
                    color="g"
                    percentage_accepted[i] += 1 
                    break 
     
            if color == "r": 
                pass

    percentage_accepted = [x / events for x in percentage_accepted]
    mean_accept = format(np.mean(percentage_accepted), ".3f")
    
    if show == False:
        return np.mean(percentage_accepted)

    print(f"({lining}) - {mean_accept}")
    plt.plot(co_tan, percentage_accepted, c="b", label = "Mean acceptance: "+mean_accept)
    
    plt.title(f"Acceptance Rate ({lining})", fontsize = '20')
    plt.xlabel("dZ/dr", fontsize = '16')
    plt.ylabel("Acceptance Probability", fontsize = '16')
    plt.legend(fontsize = '16')
    if savefig == True: 
        plt.savefig(f"Figures/Acceptance_Rate_({lining})")
    plt.show() 
            
def pointRepetitionFactor(lining:str = "makePatches_Projective", events=128, apexZ0 = 0, ppl = 16, savefig=False, v = 'v3', show = True): 
    """for every event, we loop through all the points in the dataset and 
        compute how many patches contain that point. The lower in general 
        the better, since this is a metric of non-wastefulness 

    Args:
        lining (str, optional): Solving method. Defaults to "makePatches_Projective".
        events (int, optional): number of wedges. Defaults to 128.
        apexZ0 (num or list, optional): z0 locations patches are generated at. Defaults to 0.
        n (int, optional): points per patch per layer. Defaults to 16.
        savefig (bool, optional): Saves figure in Figures folder if True. Defaults to False.
        v (str, optional): data version. Defaults to 'v3'.
        show (bool, optional): Set to False to just return acceptance list without plot. Defaults to True.

    Returns:
        tuple: mean PRF and standard deviation
    """

    out = []
    file = f'data/wedgeData_{v}_128.txt'
    all_data = readFile(file, events)
    
    for k in range(events): 
        env, points = all_data[k] 
        data = DataSet(env)
        data.importData(points)
        #add the 0.1 cm points
        data.add()
        #solve for cover
        cover = wedgeCover(env, data)
        cover.solve(lining=lining, apexZ0 = apexZ0, ppl = ppl, show = False)

        
        out2 = [] 
        
        for layer in range(env.num_layers): 
            for point in data.array[layer]: 
                
                num_in = 0
                for patch in cover.patches: 
                    if patch.contains_p(point, layer): 
                        num_in += 1
                        
                out2.append(num_in) 
                
    out += out2

    if show == False:
        return (format(np.mean(out), '.2f'), format(np.std(out), '.2f'))

    print(f"({lining}) mean - {format(np.mean(out), '.2f')}")
    print(f"({lining}) stdev - {format(np.std(out), '.2f')}")


        
    plt.hist(out, bins=np.arange(11) - 0.5, 
             edgecolor='black', 
             label = f"mean: {format(np.mean(out), '.2f')}, stdev: {format(np.std(out), '.2f')}",
             rwidth=0.8
            ) 
    plt.xlabel("Number of Covering Patches", fontsize = '16')
    plt.ylabel("Number of Points", fontsize = '16')
    plt.title(f"Point Repetition Factor ({lining})", fontsize = '20')
    plt.legend(fontsize = '16')
    if savefig == True:
        plt.savefig(f"Figures/Point_Repetition_Factor_({lining})")
    plt.show()
    return (format(np.mean(out), '.2f'), format(np.std(out), '.2f'))
