import jyotishyamitra as jsm

print("START")

#For input related functions
jsm.clear_birthdata()

################ Providing input birth data ####################
#providing Name and Gender
inputdata = jsm.input_birthdata(name="Dhaval Gondaliya", gender="male")

#providing Date of birth details
inputdata = jsm.input_birthdata(year="1992", month=jsm.March, day="27")

#Providing Place of birth details
inputdata = jsm.input_birthdata(place="Latipur", longitude="+70.5280", lattitude="+22.6250", timezone="+5.5")

#Providing Time of birth details
inputdata = jsm.input_birthdata(hour="11", min="55", sec="59")

################### Lets Validate Birthdata ######################
jsm.validate_birthdata()

#If Birthdata is valid then get birthdata
if(jsm.IsBirthdataValid()):
    birthdata = jsm.get_birthdata()


########### Set the output folder and name of file to save generated astrological data
if("SUCCESS" == jsm.set_output(path="d:\\jyotish", filename="astroOutput")):
    print(f'The output is : {jsm.get_output()}')
else:
    print("Given folder path doesnt exist")

############# Computing Astrological data ###############

if(jsm.reset_astrologicalData() == "SUCCESS"):  #Resetting the astrological data to clear history
    jsm.generate_astrologicalData(birthdata)    #Compute the astrological data based on new set.


print("END")
