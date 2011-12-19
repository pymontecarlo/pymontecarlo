package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.Electron;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.awt.event.ActionEvent;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

/**
 * Detector to count backscatter and transmitted electrons.
 * 
 * @author ppinard
 */
public class ElectronFractionDetector extends AbstractScatteringDetector {

    /** Number of backscattered electrons. */
    private int backscatterCount;

    /** Number of transmitted electrons. */
    private int transmittedCount;

    /** Number of primary electrons. */
    private int totalCount;



    @Override
    public void actionPerformed(ActionEvent e) {
        super.actionPerformed(e);

        switch (e.getID()) {
        case MonteCarloSS.TrajectoryEndEvent:
            totalCount++;
            break;
        default:
            break;
        }
    }



    @Override
    public void saveResults(File resultsDir, String baseName)
            throws IOException {
        File resultsFile = new File(resultsDir, baseName + ".txt");
        FileWriter writer = new FileWriter(resultsFile);
        String eol = System.getProperty("line.separator");

        writer.append("Backscatter fraction: " + getBackscatterFraction() + eol);
        writer.append("Transmitted fraction: " + getTransmittedFraction() + eol);

        writer.close();
    }



    @Override
    public void backscatterEvent(Electron electron) {
        backscatterCount++;
    }



    @Override
    public void transmittedEvent(Electron electron) {
        transmittedCount++;
    }



    /**
     * Returns the backscatter yield.
     * 
     * @return backscatter fraction
     */
    public double getBackscatterFraction() {
        return (double) backscatterCount / (double) totalCount;
    }



    /**
     * Returns the transmitted yield.
     * 
     * @return transmitted fraction
     */
    public double getTransmittedFraction() {
        return (double) transmittedCount / (double) totalCount;
    }



    @Override
    public void reset() {
        super.reset();

        backscatterCount = 0;
        transmittedCount = 0;
    }

}
