from __future__ import division, print_function

from heteromotility.hmtools import *
from heteromotility.hmstats import GeneralFeatures, MSDFeatures, RWFeatures
from heteromotility.hmtrack import *
from heteromotility.hmio import *
import pickle
import numpy as np
import pandas as pd

np.seterr(all='raise')

'''
Extracts motility feature information from provided cell locations or paths.

$ heteromotility.py --help

for usage information.
'''

class MotilityCalculator:
    def __init__(self, cells: list) -> None:
        self.cells = cells

    def get_motility_headers(self):
        motility_header = ['Well/XY', 'cell_id', 'total_distance', 'net_distance', 'linearity', 'spearmanrsq','progressivity',
        'max_speed', 'min_speed', 'avg_speed', 'MSD_slope', 'hurst_RS', 'nongauss', 'disp_var', 'disp_skew', 'rw_linearity', 'rw_netdist', 'turn_direction',
        'rw_kurtosis02', 'rw_kurtosis03', 'rw_kurtosis04', 'rw_kurtosis05', 'rw_kurtosis06', 'rw_kurtosis07',
        'rw_kurtosis08', 'rw_kurtosis09', 'rw_kurtosis10', 'avg_moving_speed01', 'avg_moving_speed02',
        'avg_moving_speed03', 'avg_moving_speed04', 'avg_moving_speed05', 'avg_moving_speed06',
        'avg_moving_speed07', 'avg_moving_speed08', 'avg_moving_speed09', 'avg_moving_speed10',
        'time_moving01', 'time_moving02', 'time_moving03', 'time_moving04', 'time_moving05',
        'time_moving06', 'time_moving07', 'time_moving08', 'time_moving09', 'time_moving10']

        return motility_header

    def get_heteromotility_parameters(self) -> pd.DataFrame:
        pickle_file = 'data/track/result.pickle'
        output_dir = 'data/track'

        cp = CellPaths( cell_ids = pickle.load( open(pickle_file, 'rb') ), sanity_px = 10000, interp_lim = 3 )    
        check_remaining_cells(cp.cell_ids)
        
        gf = GeneralFeatures(cp.cell_ids, move_thresh = 10)
        msdf = MSDFeatures(cp.cell_ids)
        rwf = RWFeatures(cp.cell_ids, gf)

        ind_outputs = single_outputs_list(cp.cell_ids, gf, rwf, msdf, output_dir, suffix=False)
        merged_list = make_merged_list(ind_outputs, gf, rwf)
    
        theta_stats_list = []
        for i in gf.tau_range:
            for j in gf.interval_range:
                theta_stats_list.append( 'mean_theta_' + str(i) + '_' + str(j) )
                theta_stats_list.append( 'min_theta_' + str(i) + '_' + str(j) )
                theta_stats_list.append( 'max_theta_' + str(i) + '_' + str(j) )

        turn_stats_list = []
        for i in gf.tau_range:
            for j in gf.interval_range:
                turn_stats_list.append( 'p_rturn_' + str(i) + '_' + str(j) )

        autocorr_stats_list = []
        for i in range(1, rwf.autocorr_max_tau):
            autocorr_stats_list.append('autocorr_' + str(i))

        motility_header = self.get_motility_headers()
        motility_header = motility_header + autocorr_stats_list
        motility_header = motility_header + turn_stats_list
        motility_header = motility_header + theta_stats_list

        return pd.DataFrame(merged_list, columns=motility_header)

    def motility_compute(self, parameters: pd.DataFrame):
        parameters = parameters[["cell_id", "total_distance", "linearity", "avg_speed"]]
        dtype = {"cell_id": int, "total_distance": float, "linearity": float, "avg_speed": float}
        parameters = parameters.astype(dtype=dtype)

        for cell in self.cells:
            if cell.number_id in parameters["cell_id"].values:
                cell.total_distance = parameters.loc[parameters["cell_id"] == cell.number_id]["total_distance"].values[0]
                cell.linearity = parameters.loc[parameters["cell_id"] == cell.number_id]["linearity"].values[0]
                cell.avg_speed = parameters.loc[parameters["cell_id"] == cell.number_id]["avg_speed"].values[0]

                if (cell.total_distance >= 0.1) and (cell.linearity >= 0.35) and (cell.avg_speed >= 0.004):
                    cell.motility = 1

                elif (0.05 <= cell.total_distance <= 0.1) and (0.35 > cell.linearity > 0.1) and (cell.avg_speed >= 0.004):
                    cell.motility = 2
                
                elif (0.06 <= cell.total_distance <= 0.1) and (cell.linearity > 0.1) and (cell.avg_speed < 0.004):
                    cell.motility = 3

                elif (cell.total_distance < 0.06) and (cell.linearity > 0.01) and (cell.avg_speed < 0.004):
                    cell.motility = 4

