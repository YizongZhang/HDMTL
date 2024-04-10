#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function, division
import numpy as np
import pandas as pd
from scipy.interpolate import griddata, interp1d
from pprz_data import pprz_message_definitions as msg

class DATA:
    """
    Data class from Paparazzi System.
    """
    def __init__(self, filename=None, ac_id=None, data_type=None, pad=10, sample_period=0.01):
        self.df_list = []
        self.filename = filename
        self.ac_id = ac_id
        self.df = None
        self.data_values = 0.
        self.data_type = data_type
        self.pad = pad
        self.sample_period = sample_period
        if self.data_type=='fault':
            self.read_msg1_bundle()
        elif self.data_type=='flight':
            self.read_msg1_bundle()
            self.read_msg2_bundle()
            self.read_msg3_bundle()
        self.find_min_max()
        self.df_All = self.combine_dataframes()
        
        
    def read_msg1_bundle(self):
        try:
            msg_name = 'attitude' ;columns=['time', 'phi','psi','theta'] ;drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Attitude msg doesnt exist ')
        try:
            msg_name= 'mode'; columns=['time','mode','1','2','3','4','5']; drop_columns = ['time','1','2','3','4','5']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print('Paparazzi Mode msg doesnt exist ')
        try:
            msg_name = 'imuaccel';columns=['time','Ax','Ay','Az']; drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' IMU Acceleration msg doesnt exist ')
        try:
            msg_name='gps';columns=['time','1','east','north','course','alt', 'vel', 'climb', '8','9','10','11'];drop_columns=['time','1','8','9','10','11']
            df = self.extract_message( msg_name, columns, drop_columns)
            df.alt = df.alt/1000.
            df.vel = df.vel/100.     #convert to m/s
            df.climb = df.climb/100. #convert to m/s
            print(' Generating 3D velocity...')
            df['vel_3d'] = df.climb.apply(lambda x: x**2)
            df.vel_3d = df.vel_3d + df.vel.apply(lambda x: x**2)
            df.vel_3d = df.vel_3d.apply(lambda x: np.sqrt(x))
#             if 1:
#                 # Calculate 3D speed (including the vertical component to the horizontal speed on ground.)
#                 print(' Calculating the 3D speed norm !')
#                 df['vel_3d1'] = df.climb.apply(lambda x: x**2)
#                 print(df.vel_3d1.any())
            self.df_list.append(df)
        except: print(' GPS msg doesnt exist ')
        try:
            msg_name = 'imugyro';columns=['time','Gx','Gy','Gz']; drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' IMU Gyro msg doesnt exist ')
        try:
            msg_name = 'fault_telemetry';columns=['time','Fault_Telemetry']; drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Fault Telemetry msg doesnt exist ')     

    def read_msg2_bundle(self):
        try:
            msg_name = 'actuators' ;columns=['time', 'S0','S1','S2'] ;drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Actuators msg doesnt exist ')
        try:
            msg_name = 'commands' ;columns=['time', 'C0','C1','C2'] ;drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Commands msg doesnt exist ')
        try:
            msg_name = 'energy_new' ;columns=['time', 'Throttle', 'Volt', 'Amp', 'Watt', 'mAh', 'Wh'] ;drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Energy_new msg doesnt exist ')            
        try:
            msg_name = 'air_data' ;columns=['time', 'Ps', 'Pdyn_AD', 'temp', 'qnh', 'amsl_baro', 'airspeed', 'TAS'] ;drop_columns = ['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Air Data msg doesnt exist ')
        try:
            msg_name = 'desired'; columns=['time','D_roll','D_pitch','D_course','D_x', 'D_y', 'D_altitude','D_climb','D_airspeed']; drop_columns=['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Desired msg doesnt exist ') 
            
    def read_msg3_bundle(self):
        try:
            msg_name = 'gust' ; columns=['time','wx','wz', 'Va_gust', 'gamma_gust', ' AoA_gust', 'theta_com_gust']; drop_columns=['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Gust msg does not exist ')
  # <message name="ROTORCRAFT_FP" id="147">
  #   <field name="east"     type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
  #   <field name="north"    type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
  #   <field name="up"       type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
  #   <field name="veast"    type="int32" alt_unit="m/s" alt_unit_coef="0.0000019"/>
  #   <field name="vnorth"   type="int32" alt_unit="m/s" alt_unit_coef="0.0000019"/>
  #   <field name="vup"      type="int32" alt_unit="m/s" alt_unit_coef="0.0000019"/>
  #   <field name="phi"      type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
  #   <field name="theta"    type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
  #   <field name="psi"      type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
  #   <field name="carrot_east"   type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
  #   <field name="carrot_north"  type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
  #   <field name="carrot_up"     type="int32" alt_unit="m" alt_unit_coef="0.0039063"/>
  #   <field name="carrot_psi"    type="int32" alt_unit="deg" alt_unit_coef="0.0139882"/>
  #   <field name="thrust"        type="int32"/>
  #   <field name="flight_time"   type="uint16" unit="s"/>
  # </message>
        try:
            msg_name = 'rotorcraft_fp' ; columns=['time','east','north', 'up', 'veast', 'vnorth', 'vup', 'phi', 'theta', 'psi', 'carrot_east', 
                                                    'carrot_north', 'carrot_up', 'carrot_psi', 'thrust', 'flight_time']; drop_columns=['time']
            self.df_list.append( self.extract_message( msg_name, columns, drop_columns) )
        except: print(' Rotorcraft_fp msg does not exist ')

        
    def get_settings(self):
        ''' Special Message used for the fault injection settings
        2 multiplicative, and 2 additive, and only appears when we change them
        so the time between has to be filled in...'''
        msg_name = 'settings'; columns=['time','m1','m2','add1','add2'];drop_columns=['time']
        df = self.extract_message( msg_name, columns, drop_columns)
        df.add1 = df.add1/9600. ; df.add2 = df.add2/9600.
        
        return df
       
    def extract_message(self, msg_name, columns, drop_columns):
        ''' Given msg names such as attitute, we will call msg.read_log_attitute'''
        exec('self.data_values = msg.read_log_{}(self.ac_id, self.filename)'.format(msg_name))
        df = pd.DataFrame(self.data_values, columns=columns)
        df.index = df.time
        df.drop(drop_columns, axis=1, inplace=True)
        print(df)
        return df
        
    def find_min_max(self):
        self.min_t = 1000.
        self.max_t = -1.
        for df in self.df_list:
            self.min_t = min(self.min_t, min(df.index))
            self.max_t = max(self.max_t, max(df.index))
        print('Min time :',self.min_t,'Maximum time :', self.max_t) # Minimum time can be deceiving... we may need to find a better way.

    def linearize_time(self, df, min_t=None, max_t=None):
        if (min_t or max_t) == None:
            min_t = min(df.index)
            max_t = max(df.index)
        time = np.arange(int(min_t)+self.pad, int(max_t)-self.pad, self.sample_period)#重新定义新的时间轴，时间点对齐
        out = pd.DataFrame()
        out['time'] = time
        
        for col in df.columns:
            func = interp1d(df.index , df[col]) # FIXME : 插值，数据点对齐.
            
            out[col] = func(time)
            
            
        out.index = out.time
        out.drop(['time'], axis=1, inplace=True)

        return out
    
    def combine_dataframes(self):
        frames = [self.linearize_time(df, self.min_t, self.max_t) for df in self.df_list]
        return pd.concat(frames, axis=1, ignore_index=False, sort=False)

    def combine_settings_dataframe(self):
        df_settings = self.get_settings() #FIXME : we may check if this has been already done before or not...
        return pd.concat(([self.df_All, df_settings]), axis=1, ignore_index=False, sort=False)

    def get_labelled_data(self):
        df = self.combine_settings_dataframe()
        df.m1.iloc[0] = 1.0
        df.m2.iloc[0] = 1.0
        df.add1.iloc[0] = 0.0
        df.add2.iloc[0] = 0.0
        return df.ffill()
