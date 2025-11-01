# :brain: Whatcha Thinkin? 

Whatcha thinkin is a brain computer inference that allows the user to control a 2d side scroller game using a custom-built EEG circuit. The user attaches the 3 electrodes, 2 on the forehead and one on the earlobe and runs the game and EEG reading scripts. The game will run and then begin being controlled by the user's brainwaves. 

Video demonstration of the project: [Live Demonstration](https://www.youtube.com/watch?v=aFaplhdCCEs)




## :wrench: How is it made?

1. [Circuit Design](#Circuit-Design)
2. [Game Design](#Game-Design)

   
## :robot: Circuit Design

1. [Hardware Design](#Hardware-Design)
2. [Reading EEG Signals](#Reading-EEG-Signals)

### :satellite: Hardware Design
Firstly, I would like to give proper credit to the original designer for the EEG circuit that I modified for this project. It can be found here: [EEG Circuit](https://www.instructables.com/DIY-EEG-and-ECG-Circuit/). Feel free to read it if you would like an even more in-depth explanation of it, and/or a price list if you wanted to create your own.

But here is a general overview explanation of how the modified version for my project works. My circuit can be broken down into 7 main components:

1. **Amplification**
- Most crucial part of the circuit. This is where we actually read the EEG signals from the brain. The user attaches an electrode to the earlobe, which serves as our grounding electrode. The other two input electrodes are attached onto the forehead, which would be represented as Fp1 & Fp2 on an EEG node map. These nodes work best for the simplified nature of our machine. The reason that this section is the most important part is because EEG signals are very accute and thus we need a strong amplifier to be able to capture the signals properly. If the amp stage is not working, then the entire project does not. 

2. **1st 60hz Notch filter**
- Sections 2-6 serve to clean up and remove any possible noise, as it is important that our signal is represented accurately. As for the filter itself, it is designed to filter out the biggest source of noise in our circuit due to power line interference.

3. **7hz High Pass filter**
- This filter's purpose is to remove any galvanic skin response from the head. We want to account for the potential change of electrical properties of skin from factors such as sweat or oily skin.

4. **40hz Low Pass filter**
- This filter ensures that we aren't reading any waves above 40hz as it is unnecessary and could contain noise. For the project, I chose to limit movement to a binary choice. Thus, I chose the 2 brainwaves out of 5 that had the most common activations and hertz ranges. That being Beta(12-30hz) & Gamma(30+hz). Thus anything higher than 40hz was not needed. This also has the added benefit of removing any potential muscle movements from, say, the eyebrows. 

5. **1 hz High pass filter**
- Similarly, along the lines of the previous filter. Instead of removing any extreme high-end frequencies, we do the same for low-end frequencies.

6. **2nd 60Hz Notch filter & gain stage**
- Unfortunately, I was unable to implement a 120hz filter to achieve a cascading power line removal system. So, I added another 60hz filter and a potentiometer to control gain. To either strengthen or weaken the signal.

7. **Analog to Digital Conversion**
- This section is pretty self-explanatory. We use a part known as the ADS1115 for its differential mode. This allows us to measure the difference in voltage between our filtered signal and our ground. Which offers even another layer of noise cancellation. The ADS is also able to more precisiely capture signals than the arudino. Making it the perfect low cost effective part to convert our signal from analog to digital. 
### :bar_chart: Reading EEG Signals

Now that we've actually derived a signal from the brain, we need to extrapolate the 2 wavelengths that we want. Thats where **EEG_collection.ino** comes into play. The program reads EEG signal data from our ADS1115, removes DC offset noise, and applies a digital Butterworth bandpass filter to isolate brainwave frequencies (roughly 8–100 Hz). It then continuously outputs the raw, converted, and filtered signal values over the serial connection for analysis. Now that we've collected our data, we need to process it further. Which of course takes place in **EEG_processing.py** & **modified_eeg_processing.py**. In the original file, we establish a serial connection at 115200 baud rate on COM3 and continuously read data packets containing the readings from the previous file. We maintain 2 circular buffers with a max size of 512 samples to store the EEG data and corresponding timestamps. It runs a background thread that reads the incoming data and parses each line to extract the filtered EEG values. Then we visualize it using matplotlib to display 3 subplots in real-time using animation. The first plot shows the EEG signal amplitude in microvolts against time. The second displays the frequency spectrum computed using Fast Fourier transform with a Hanning window. The third shows bar charts representing the power levels of Gamma and Beta waves, respectively. The visualization updates every 100 milliseconds to provide a buffer but still provide near real-time feedback. 

The modified version uses the same core logic but has built on logic to allow interprocess communication to share the EEG data with our game. That being our bridge file called **Shared_data**. We import our EEGDataBridge which serves as the communciation interface between the EEG processing script and our game. This file stores beta and gamma power values, along with flags indicating whether the EEG processor and the game are running. After each update, the script writes new brainwave data and reads the game’s status to display a visual indicator, yellow when inactive and lime green when connected. The program initializes and cleans up the data bridge by sending zero values at startup and shutdown to signal connection states. 
## :video_game: Game Design
Now I won't get too much into the design of the game itself, as it's just a simple 2d side scroller with a level editor. I will discuss **modified_game.py**. The file's main function is to replace the standard WASD & space controls with our EEG input. We import the EEGDataBridge class to communicate with the EEG processing script, which signals when the game starts and stops. Two sensitivity thresholds, that being beta_threshold and gamma_threshold (are both set to 400) determine when brain activity triggers movement. Gameplay is now driven by the process_eeg_input function, which reads the brainwave data from the shared JSON file each frame. Low beta activity moves the character left, while high beta activity moves right. Likewise, high gamma activity causes a jump when allowed. While the use_eeg_control flag allows switching between EEG and keyboard movements. The player can then press tab to toggle between EEG and keyboard input.  Note that there is a delay when this occurs. Since we have a buffer for reading the EEG input data, it takes a moment for the remaining data to finish being read. Speaking of cooldown timers, we have one implemented to prevent repeated jumps from high gamma activity. And on the screen we display the EEG connection status and control mode. The also panel showcases connection status. It highlights the top text green for connected and red for disconnected..


## :bookmark_tabs: Lessons Learned
This project was easily one of my favorites I've worked on in my college career. I mean, how many people can say that they made a device that lets you play games using your mind? With the caveat of it not being that great. But noneless, I learned a great deal from this project. First and foremost being the hands on experience of learning electrical engineering. While I did not design the circuit from scratch, building it in person did provide a huge learning experience. Suffice to say, I will never ever be touching a circuit again. Kidding, but it was a pain in the butt having to troubleshoot power failures, and the need to have to keep buying replacement parts. However, in the end, I was able to get the project up and running again. The next thing I learned was actually my passion for the human brain. The semester that I created this project (I am retroactively writing this readme) saw me working on a project that actually used computer vision techniques, namely segmentation, to highlight tumor areas in an MRI. You can find that [Here](https://github.com/Er1ckD1az/TumorHighlightingUsingSegmentation). This sparked my interest in the human brain as I think its easily the most fascinating human organ. Then there was of course the usual learning better coding habits, new libraries, etc. All the jazz that you undergo when taking up a project. But my 2 biggest take aways were my newfound distain for electrical engineering and love for the human brain. 

Again, if you would like to see the project in action. Please watch the video [here](https://www.youtube.com/watch?v=aFaplhdCCEs)
