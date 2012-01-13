package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.Electron;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;

import java.awt.event.ActionEvent;
import java.io.IOException;
import java.util.zip.ZipOutputStream;

import org.jdom.Element;

import pymontecarlo.util.ZipUtil;

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
    public void saveResults(ZipOutputStream zipOutput, String key)
            throws IOException {
        // Create XML
        Element element = new Element("result");

        Element child = new Element("backscattered");
        child.setAttribute("val", Double.toString(getBackscatterFraction()));
        element.addContent(child);

        child = new Element("transmitted");
        child.setAttribute("val", Double.toString(getTransmittedFraction()));
        element.addContent(child);

        // Save CSV in ZIP
        ZipUtil.saveElement(zipOutput, key + ".xml", element);
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



    @Override
    public String getPythonEquivalent() {
        return "pymontecarlo.result.base.result.ElectronFractionResult";
    }

}
