# Whatcha Thinkin? 

Whatcha thinkin is a brain computer inference that allows the user to control a 2d side scroller game using a custom built EEG circuit. The user attaches the 3 electrodes, 2 on the forehead and one on an ear lob and runs the game and EEG reading scripts. The game will run and then begin being controlled by the users brainwaves. 

Video demonstration of the project: [Live Demonstration](https://www.youtube.com/watch?v=aFaplhdCCEs)




## How is it made?

1. link to circuit design
2. link to game design
## Circuit Design
1. HardWare Design
2. Reading EEG signals

### Hardware Design
Firstly I would like to give proper credit to the original designer for the EEG circuit that I modifidy for this project. It can be found here: (EEG Circuit)[https://www.instructables.com/DIY-EEG-and-ECG-Circuit/] Feel free to read it if you would like an even more indepth explanation of it and price list if you wanted to create your own.

But here is a general overview explanation of how the modifidied version for my project works. My circuit can be broken down into 7 main components:

1. Amplification
- Most crucial part of the circuit. This is where we actually read the EEG signals from the brain. The user attaches an electrode onto the earlobe which serves as our grounding electrode. The other two input electrodes are attached onto the forehead which would be represented as Fp1 & Fp2 on an EEG node map. These nodes work best for the simplifed nature of our machine. The reason that this section is the most important part is because EEG signals are very accute and thus we need a strong amplifier to be able to capture the signals properly. If the amp stage is not working, then the entire project does not. 

2. 1st 60hz Notch filter
- Sections 2-6 serve to clean up and remove any possible noise, as it is important that our signal is represented accurately. As for the filter itself, it is designed to filter out the biggest source of noise in our circuit due to power line interference.

3. 7hz High Pass filter
- This filter's purpose is to remove any galvanic skin response from the head. We want to account for the potential change of electrical properties of skin from factors such as sweat or oily skin.

4. 40hz Low Pass filter
- This filter ensures that we aren't reading any waves above 40hz as it is unnecessary and could contain noise. For the project I chose to limit movement to a binary choice. Thus I chose the 2 brainwaves out of 5 that had the most common activations and hz ranges. That being Beta(12-30hz) & Gamma(30+hz). Thus anything higher than 40hz was not needed. This also has the added benefit of removing any potiental muscle movements from say, the eyebrows. 

5. 1 hz High pass filter
- Similiarly along the lines of the previous filter. Instead of removing any extreme high end frequencies, we do the same for low end frequencies.

6. 2nd 60Hz Notch filter & gain stage
- Unfortunately I was unable to implement a 120hz filter to achieve a cascading power line remove system. So, I added another 60hz filter and a potentiometer to control gain. To either stregnthen or weaken the signal.

7. Analog to Digital Conversion
- This sections is pretty self explanatory. We use a part known as the ADS1115 for its differential mode. Which allows us to measure the difference in voltage between our filtered signal and our ground. Which offers even another layer of noise cancelation. The ADS also is able to more precisiely capture signals than the arudino. Making it the perfect low cost effective part to convert our signal from analog to digital. 

### Reading EEG Signals

Now that we've actually derived a signal from the brain we need to exprapalate the 2 wave lenths that we want. 
## Game Design
