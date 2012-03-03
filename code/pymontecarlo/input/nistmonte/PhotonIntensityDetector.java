package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.EPQLibrary.Element;
import gov.nist.microanalysis.EPQLibrary.ToSI;
import gov.nist.microanalysis.EPQLibrary.XRayTransition;
import gov.nist.microanalysis.EPQLibrary.XRayTransitionSet;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayAccumulator;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.io.IOException;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.zip.ZipOutputStream;

import ptpshared.opencsv.CSVWriter;
import pymontecarlo.util.ZipUtil;

/**
 * Detector to record intensity of photons.
 * 
 * @author ppinard
 */
public class PhotonIntensityDetector extends PhotonDetector {

    /** Stores the <code>XRayAccumulator</code> for each element. */
    private XRayAccumulator xrayAccumulator = null;



    @Override
    protected void saveAsProperties(Properties props) {
        super.saveAsProperties(props);

        Set<Element> elements = new HashSet<Element>();
        for (XRayTransition xrayTransition : xrayAccumulator.getTransitions()) {
            elements.add(xrayTransition.getElement());
        }
        props.setProperty("accumulators", elements.toString());
    }



    /**
     * Creates a new <code>PhotonIntensityDetector</code>.
     * 
     * @param takeOffAngle
     *            elevation from the x-y plane (in radians)
     * @param azimuthAngle
     *            counter-clockwise angle from the positive x-axis in the x-y
     *            plane (in radians)
     */
    public PhotonIntensityDetector(double takeOffAngle, double azimuthAngle) {
        super(takeOffAngle, azimuthAngle);
    }



    /**
     * Creates a new <code>PhotonIntensityDetector</code>.
     * 
     * @param position
     *            detector position in the chamber (in meters)
     */
    public PhotonIntensityDetector(double[] position) {
        super(position);
    }



    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) throws EPQException {
        double e0 = ToSI.eV(50);
        double emax = mcss.getBeamEnergy();

        List<XRayTransition> xrayTransitions = new ArrayList<XRayTransition>();
        for (Element element : mcss.getElementSet()) {
            xrayTransitions.addAll(new XRayTransitionSet(element, e0, emax)
                    .getTransitions());
        }

        xrayAccumulator = new XRayAccumulator(xrayTransitions);
        xrel.addActionListener(xrayAccumulator);
    }



    @Override
    public void saveResults(ZipOutputStream zipOutput, String key)
            throws IOException {
        // Create CSV
        StringWriter sw = new StringWriter();
        CSVWriter writer = new CSVWriter(sw);

        writer.writeNext("transition", "energy (eV)",
                "generated characteristic", "generated characteristic unc",
                "generated bremsstrahlung", "generated bremsstrahlung unc",
                "generated no fluorescence", "generated no fluorescence unc",
                "generated total", "generated total unc",
                "emitted characteristic", "emitted characteristic unc",
                "emitted bremsstrahlung", "emitted bremsstrahlung unc",
                "emitted no fluorescence", "emitted no fluorescence unc",
                "emitted total", "emitted total unc");

        List<XRayTransition> xrayTransitions = new ArrayList<XRayTransition>();
        xrayTransitions.addAll(xrayAccumulator.getTransitions());
        Collections.sort(xrayTransitions);

        String xrayTransitionName;
        double emittedIntensity;
        double generatedIntensity;
        double xrayTransitionEnergy;
        for (XRayTransition xrayTransition : xrayTransitions) {
            xrayTransitionName =
                    xrayTransition.getElement().toAbbrev() + " "
                            + xrayTransition.getIUPACName();

            try {
                xrayTransitionEnergy = xrayTransition.getEnergy_eV();
            } catch (EPQException e) {
                xrayTransitionEnergy = 0.0;
            }

            emittedIntensity = xrayAccumulator.getEmitted(xrayTransition);
            generatedIntensity = xrayAccumulator.getGenerated(xrayTransition);

            writer.writeNext(xrayTransitionName, xrayTransitionEnergy, 0.0,
                    0.0, 0.0, 0.0, generatedIntensity, 0.0, generatedIntensity,
                    0.0, 0.0, 0.0, 0.0, 0.0, emittedIntensity, 0.0,
                    emittedIntensity, 0.0);
        }

        writer.close();

        // Save CSV in ZIP
        ZipUtil.saveStringBuffer(zipOutput, key + ".csv", sw.getBuffer());
    }



    @Override
    public boolean requiresBremsstrahlung() {
        return false;
    }



    @Override
    public String getPythonEquivalent() {
        return "pymontecarlo.result.base.result.PhotonIntensityResult";
    }



    @Override
    public void reset() {
        xrayAccumulator.clear();
    }

}
