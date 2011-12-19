package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Listener to record the time elapsed of a simulation.
 * 
 * @author ppinard
 */
public class TimeDetector extends AbstractDetector implements ActionListener {

    /** System time when the simulation started. */
    private long startSimulationTime;

    /** System time when the simulation ended. */
    private long elapsedTime;

    /** System time when a trajectory starts. */
    private long startTrajectoryTime;

    /** Sum of the trajectory times. */
    private double sum;

    /** Square sum of the trajectory times. */
    private double sumSquare;

    /** Number of trajectories. */
    private double count;



    @Override
    public void actionPerformed(ActionEvent ae) {
        switch (ae.getID()) {
        case MonteCarloSS.FirstTrajectoryEvent:
            startSimulationTime = System.currentTimeMillis();
            elapsedTime = 0;

            sum = 0;
            sumSquare = 0;
            count = 0;
            break;
        case MonteCarloSS.LastTrajectoryEvent:
            elapsedTime = System.currentTimeMillis() - startSimulationTime;
            break;
        case MonteCarloSS.TrajectoryStartEvent:
            startTrajectoryTime = System.currentTimeMillis();
            break;
        case MonteCarloSS.TrajectoryEndEvent:
            long trajectoryTime =
                    System.currentTimeMillis() - startTrajectoryTime;
            sum += trajectoryTime;
            sumSquare += trajectoryTime * trajectoryTime;
            count += 1;
        default:
            break;
        }

    }



    /**
     * Returns the elapsed time to run the simulation in milliseconds.
     * 
     * @return elapsed time in milliseconds
     */
    public long getElapsedtime() {
        return elapsedTime;
    }



    /**
     * Returns the average time for a trajectory.
     * 
     * @return average trajectory time
     */
    public double getTrajectoryTimeAverage() {
        return sum / count;
    }



    /**
     * Returns the variance of the trajectory time.
     * 
     * @return trajectory time variance
     */
    public double getTrajectoryTimeVariance() {
        double average = getTrajectoryTimeAverage();
        return sumSquare / count - average * average;
    }



    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) throws EPQException {
        mcss.addActionListener(this);
    }



    @Override
    public void saveResults(File resultsDir, String baseName)
            throws IOException {
        File resultsFile = new File(resultsDir, baseName + ".txt");
        FileWriter writer = new FileWriter(resultsFile);
        String eol = System.getProperty("line.separator");

        writer.append("Simulation time: " + getElapsedtime() / 1000.0 + " s"
                + eol);

        writer.append("Average trajectory time: " + getTrajectoryTimeAverage()
                + " +- " + Math.sqrt(getTrajectoryTimeVariance()) + " ms");

        writer.close();
    }
}
