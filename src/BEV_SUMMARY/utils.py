import sqlite3
import os





def method_1(C_A_F_Y,T_A_F_Y,C_L_Y_Y,T_L_F_Y):
    rt= [(C_A_F_Y + T_A_F_Y ) - (C_L_Y_Y + T_L_F_Y) for C_A_F_Y,T_A_F_Y,C_L_Y_Y,T_L_F_Y in zip(C_A_F_Y,T_A_F_Y,C_L_Y_Y,T_L_F_Y) ]
 
    result_1 = rt[0]
    result_2  = rt[1]
    result_3  = rt[2]
    final_result = result_1*0.5 +    result_2*0.5 + result_3*0.25

    return result_1,result_2,result_3,final_result 



def method_2(fcf: list, discount_rate: float, growth_rate: float, terminal_year: int,current_liabilities:list):
    # Convert growth_rate to float if it is a string
    growth_rate = float(growth_rate)
    
    # Calculate discounted FCFs
    # discounted_fcf = [fcf[t] / ((1 + discount_rate) ** (t + 1)) for t in range(len(fcf))]

    projected_fcf = [((fcf_value*0.7) - (current_l))*discount_rate for fcf_value,current_l in zip(fcf,current_liabilities)]
    
    # Calculate terminal value with correct float handling
    terminal_value = (fcf[0] * (1 + growth_rate)) / abs((discount_rate - growth_rate))
    
    # Calculate discounted terminal value
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** terminal_year)
    
    # Calculate total value
    total_value = sum(projected_fcf) + discounted_terminal_value
    
    return round(total_value,2), projected_fcf, discounted_terminal_value

def method_3(revenue,expense,PE_Ratio):
    net_profits = [revenue - expense for revenue, expense in zip(revenue, expense)]
    result_net = [i*PE_Ratio for i in net_profits]

    return net_profits,result_net


def method_4(revenues,Industry_Multiplier):
    gross_rev = [i*Industry_Multiplier for i in revenues]

    return gross_rev


def method_5(revenue,expense,Earnings_Multiplier):
    
    net_profits = [revenue - expense for revenue, expense in zip(revenue, expense)]
    result_net = [i*Earnings_Multiplier for i in net_profits]

    return net_profits,result_net
    

def method_6(current_asset,current_liabilites):
    net_profits = [current_asset - current_liabilites for current_asset, current_liabilites in zip(current_asset, current_liabilites)]
    return net_profits
    


def get_data_sql( Industry_Name:str) :
    conn = sqlite3.connect(os.path.join('artifacts','BEV_database.db'))
    cursor = conn.cursor()
    query = f"SELECT * FROM BEV WHERE Industry_Name = '{Industry_Name}';"
    cursor.execute(query )
    result = cursor.fetchone()

    # df_from_db = pd.read_sql(sql=query,con= conn)
    # conn.close()

    return result
